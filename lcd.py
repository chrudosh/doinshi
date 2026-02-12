import utime
class Lcd_i2c:
    LCD_ADDR = 0x3E

    CLEAR_DISPLAY = 0x01
    RETURN_HOME   = 0x02
    ENTRY_MODE_SET= 0x04
    DISPLAY_CTRL  = 0x08
    CURSOR_SHIFT  = 0x10
    FUNCTION_SET  = 0x20
    SET_CGRAM_ADDR= 0x40
    SET_DDRAM_ADDR= 0x80

    ENTRY_LEFT    = 0x02
    DISPLAY_ON    = 0x04
    CURSOR_OFF    = 0x00
    BLINK_OFF     = 0x00
    _2LINE        = 0x08
    _5x8DOTS      = 0x00

    def __init__(self, i2c, cols=16, rows=2):
        self.i2c = i2c
        self.cols = cols
        self.rows = rows
        utime.sleep_ms(50)
        self._cmd(self.FUNCTION_SET | self._2LINE | self._5x8DOTS)
        utime.sleep_ms(5)
        self.display_on(True)
        self.clear()
        self._cmd(self.ENTRY_MODE_SET | self.ENTRY_LEFT)
        utime.sleep_ms(2)

    def _cmd(self, cmd):
        try:
            self.i2c.writeto(self.LCD_ADDR, bytes([0x80, cmd]))
        except OSError:
            pass

    def _data(self, data_byte):
        try:
            self.i2c.writeto(self.LCD_ADDR, bytes([0x40, data_byte]))
        except OSError:
            pass

    def clear(self):
        self._cmd(self.CLEAR_DISPLAY)
        utime.sleep_ms(2)

    def home(self):
        self._cmd(self.RETURN_HOME)
        utime.sleep_ms(2)

    def display_on(self, on=True):
        self._cmd(self.DISPLAY_CTRL | (self.DISPLAY_ON if on else 0) | self.CURSOR_OFF | self.BLINK_OFF)

    def set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.rows:
            row = self.rows - 1
        addr = col + row_offsets[row]
        self._cmd(self.SET_DDRAM_ADDR | addr)

    def write(self, s):
        if isinstance(s, str):
            s = s.encode('latin-1', 'replace')
        for b in s:
            self._data(b)

    def create_char(self, location, bitmap8):
        location &= 0x7
        base = location << 3
        self._cmd(self.SET_CGRAM_ADDR | base)
        for row in bitmap8[:8]:
            self._data(row & 0x1F)