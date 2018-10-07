# pip install pyserial

import serial,time,math
import serial.tools.list_ports as stlp

def choose_serial_connection():
    l = stlp.comports()
    if len(l) == 0:
        raise Exception('No available serial devices found')

    print('Please choose from the following serial ports.')
    for i,s in enumerate(l):
        print('({}) {}'.format(i,s))

    k = input('Please enter a number [{}-{}]'.format(0, len(l)-1))
    k = k.strip()
    if len(k)==0: k=0
    return l[int(k)].device

class grbl:
    def __init__(self, name=None, verbose=True):
        if name is None:
            print('(grbl)looking for serial connections.')
            name = choose_serial_connection()

        self.ser = serial.Serial(name,115200,timeout=0.2)
        print('(grbl)serial name: ',self.ser.name)
        self.linenumber = 0

        self.default_timeout = None
        self.verbose = verbose

        self.init_offset()
        self.waitready()

    def debug(self, *a):
        if self.verbose:
            print(*a)

    def readline(self):
        b = self.ser.readline()
        return b.decode('ascii')[:-2] # cutoff \r\n

    def command(self,string):
        self.debug('(grbl) SENT: '+string)
        b = (string+'\n').encode('ascii')
        self.ser.write(b)
        self.ser.flush()

        self.linenumber+=1

    def wait(self, string, timeout=None, length=0):
        current = time.time()
        collected_lines = []
        self.debug('(grbl) waiting for "'+ string+'"')
        while 1:
            if timeout is not None:
                if time.time() - current > timeout:
                    raise Exception('(grbl) waited longer than '+str(timeout))

            line = self.readline()
            if len(line)>0:
                current = time.time()
                self.debug('(grbl) RECV: "{}"'.format(line))
                collected_lines.append(line)
                self.errorfilter(line) # check to see if any errors were returned
                if (length==0 and line == string) or (length>0 and line[0:length] == string):
                    return collected_lines
            else:
                pass

    def errorfilter(self, string):
        if 'error:' in string:
            eid = string[6:].strip()

            from .errors import errors

            if eid in errors:
                raise Exception('(grbl) ERROR:{}({})"'.format(
                    eid, errors[eid]))
            else:
                raise Exception('(grbl) UNKNOWN ERROR ({})'.format(eid))

        if 'ALARM:' in string:
            eid = string[6:].strip()

            from .errors import alarms
            if eid in alarms:
                raise Exception('(grbl) ALARM:{}({})"'.format(
                    eid, alarms[eid]))
            else:
                raise Exception('(grbl) UNKNOWN ALARM ({})'.format(eid))


    def waitok(self,timeout=None):
        return self.wait('ok',timeout)

    def waitready(self):
        while 1:
            try:
                self.command('$X') # clear status
                self.wait('ok', timeout=1, length=2)
                self.debug('(grbl) Machine Ready.')
            except Exception as e:
                print(e)
            else:
                return

    # send command and wait for ok.
    def command_ok(self,c,timeout=None):
        self.command(c)
        return self.waitok(timeout)

    # use default timeout value
    def command_ok_default(self,c):
        return self.command_ok(c, self.default_timeout)

    def send(self,c): return self.command_ok_default(c)

    # below APIs are for users

    # always do homing on start.
    def home(self):
        self.debug('(grbl) Homing...')
        self.command_ok_default('$H') # homing

    def goto(self, x=None, y=None, z=None, f=None):
        # f means feedrate(mm/min)
        # use 50000 for free movement; 2000 for plotting

        # there is no need to limit speed of free movement since that's already limited by settings stored in the microcontroller EEPROM

        cmd = 'G1'
        if f is not None: cmd += 'F{:.2f}'.format(f)
        if x is not None: cmd += 'X{:.2f}'.format(x+self.offset[0])
        if y is not None: cmd += 'Y{:.2f}'.format(y+self.offset[1])
        if z is not None: cmd += 'Z{:.2f}'.format(z+self.offset[2])

        self.command_ok_default(cmd)

    # helper for offseting the coordinate system.
    def init_offset(self):
        self.set_offset(0,0,0)

    # add an offset to the bot.
    def set_offset(self, x=None, y=None, z=None):
        def n2z(x): return 0 if x is None else x
        self.offset = [n2z(k) for k in [x,y,z]]

    def set_speed(self, speed):
        if speed<=0: raise Exception('speed less than or equal to zero ({})'.format(speed))
        self.command_ok_default('G1 F{:.2f}'.format(speed))

    # obtain status word from machine
    def status_report(self):
        self.command('?')
        lines = self.wait('<', timeout=10, length=1)
        line = lines[-1]
        import re
        return re.match(r'\<(.*?)\|', line).group(1)

    # wait for all commands in buffer finish execution
    def wait_until_idle(self):
        while self.status_report().lower() != 'idle':
            time.sleep(0.5)
            pass

    def join(self):return self.wait_until_idle()
    def sync(self):return self.join()
