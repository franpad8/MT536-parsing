""" Parseo de mensaje MT536 de Swift """
import re

# Current set languaje. 0 for Spanish, 1 for English.
LANGUAGE = 0

### Exception Handling Definition ###


class ParsingException(Exception):
    """ Custom Exception Class for Parsing Errors """
    pass

### Build specific format error ###
def buildErrMsg(code, line, **kargs):
    if code in [0, 5]:
        msg = (error_dict[code][LANGUAGE]) % (line)
    elif code in [1, 11]:
        msg = (error_dict[code][LANGUAGE]) % (line, kargs["tag"])
    elif code in [2, 3]:
        msg = (error_dict[code][LANGUAGE]) % (line, kargs["value"])
    elif code == 4:
        msg = (error_dict[code][LANGUAGE]) % (
            line, kargs["field_name"], kargs["value"])
    elif code == 6:
        msg = (error_dict[code][LANGUAGE]) % (
            line, kargs["subfield_name"], kargs["value"])
    elif code == 7:
        msg = (error_dict[code][LANGUAGE]) % (line, kargs[
            "field_name"], kargs["option"], kargs["pattern"])
    elif code == 8:
        msg = (error_dict[code][LANGUAGE]) % (line, kargs["field_name"], kargs["subfield_name"],
                                              kargs["pattern"])
    elif code == 9:
        msg = (error_dict[code][LANGUAGE]) % (line, kargs["field_name"], kargs["qualifier_value"],
                                              kargs["subfield_name"], kargs["subfield_value"])
    elif code == 10:
        msg = (error_dict[code][LANGUAGE]) % (
            line, kargs["field_name"], kargs["qualifier_value"])
    else:
        msg = (error_dict[0][LANGUAGE]) % (line)
    return msg

### Define dictionary of errors with respective languages ###
error_dict = {
    0: {
        0: "Error de sintaxis en linea %s.",
        1: "Sintax error in line %s."
    },
    1: {
        0: "Error de sintaxis en linea %s. Este campo debe contener la etiqueta \'%s\'.",
        1: "Sintax error in line %s. This field must have the tag \'%s\'."
    },
    2: {
        0: "Error código T92 en la linea %s. Este campo debe contener el codigo %s.",
        1: "Error code T92 at line %s. This field must contain the code %s."
    },

    3: {
        0: ("Error código T97 en la linea %s."
            "El Indicador de Continuación debe contener uno de los"
            "siguientes valores: %s."),
        1: ("Error code T97 at line %s."
            "Continuation Indicator must contain one of the"
            "following codes: %s.")
    },
    4: {
        0: ("Error código T89 en la linea %s. "
            "El calificador del campo '%s' debe contener uno de los siguientes valores: %s."),
        1: ("Error code T89 at line %s. "
            "'%s' Field Qualifier must contain one of the"
            "following codes: %s.")
    },
    5: {
        0: ("Error en la linea %s."
            " Código con mal formato."),
        1: ("Error at line %s."
            " Bad format code")
    },

    6: {
        0: ("Error en la linea %s. "
            "El subcampo %s, debe contener uno de los siguientes valores:"
            " %s."),
        1: ("Error at line %s. "
            "Subfield \'%s\', must contain one of the following codes:"
            " %s."),
    },
    7: {
        0: ("Error en la linea %s. "
            "El campo %s, opción %s,  debe contener el siguiente formato:"
            " \'%s\'"),
        1: ("Error at line %s. "
            "%s field, option %s, must contain the following format:"
            " \'%s\'"),
    },

    8: {
        0: ("Error en la linea %s. "
            "En el campo \'%s\', el subcampo \'%s\' debe contener el siguiente formato:"
            " \'%s\'"),
        1: ("Error at line %s. "
            "In \'%s\' field, subfield \'%s\' must contain the following format:"
            " \'%s\'"),
    },

    9: {
        0: ("Error en la linea %s. "
            "En el campo '%s', si el calificador es '%s' y Data Source Scheme no esta presente "
            "entonces el subcampo '%s' debe contener uno de los siguientes valores: %s."),
        1: ("Error at line %s. "
            "In field '%s', If Qualifier is '%s' and Data Source Scheme is not present then "
            "subfield '%s' must contain one of the following codes: %s.")
    },
    10: {
        0: ("Error en la linea %s. "
            "Un campo '%s' con calificador igual a '%s' debe estar presente en este mensaje."),
        1: ("Error code in line %s. "
            " A '%s' field with Qualifier value '%s' is mandatory in this message.")
    },
    11: {
        0: "Error en la linea %s. Este campo solo acepta las siguientes opciones '%s'.",
        1: "Error at line %s. This fields only accepts one of the following options '%s'."
    },
}

### Defined REGEXs ###
tagp = ':[0-9]{2}[A-Z]:'
fsetalphanum = "[A-Z0-9]+"
fsetalpha = "[A-Z]+"
setx = "[A-Za-z0-9\/-?:(.,)'+]"
fbic = "[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?"
fdate = '(?P<date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))'
fdate1 = '(?P<date1>(?P<year1>\d{4})(?P<month1>\d{2})(?P<day1>\d{2}))'
ftime = '(?P<time>(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2}))'
ftime1 = '(?P<time1>(?P<hour1>\d{2})(?P<min1>\d{2})(?P<sec1>\d{2}))'
fdecimalutc = '(,(?P<decimals>\d{1,3}))?(\/(?P<sign>N)?(?P<utch>\d{2}(?P<utcm>\d{2})?))?'
fcorrectdate = '\d{4}(0[1-9]|1[0-2])([0-2][1-9]|3[0-1])'
fcorrecttime = '([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])'

def alpha(size):
    return "[A-Z]{1,%s}" % size

def alphaFixed(size):
    return "[A-Z]{%s}" % size

def alphanum(size):
    alphanum = '[A-Z0-9]' + "{1,%s}" % (size)
    return alphanum

def alphanumFixed(size):
    return '[A-Z0-9]{%s}' % (size)

def num(size):
    """ Return a Regex for numbers of length equal or less to a given size """
    return '\d{1,%s}' % (size)

def decimal(size):
    """ Return a Regex for decimal numbers of length equal or less to a given size """
    return r'\d{1,%s},\d*'%size

def fsetx(size):
    """ Return a Regex for setx of length equal or less to a given size """
    return '((?!.*\/\/.*)(?!\/)%s{1,%s}(?<!/))' % (setx, size)

### Format Verifications routines ###

def isCorrectDate(date):
    """ Verify if a given date is format valid """
    if re.match(fcorrectdate, date):
        return True
    return False

def isCorrectTime(time):
    """ Verify if a given time is format valid """
    if re.match(fcorrecttime, time):
        return True
    return False

def isCorrectUTC(sign, utch, utcm):
    """ Verify if a given UTC is format valid """
    if not utch is None and not re.match('[0-1][0-9]|2[0-3]', utch):
        return False
    else:
        if not utcm is None:
            if not re.match('[0-5][0-9]', utcm):
                return False
    return True

def isSwiftFieldFormatValid(word):
    if re.match('%s(.+)'%tagp, word):
        return True
    else:
        return False

def isalphanumStrict(word, size):
    """ Given a word and a size value, Returns True if the word is alphanumeric sequence 
    of length equal to the given size """
    return re.match(alphanumFixed(size), word)

def isalphanum(word, size):
    """ Given a word and a size value, Returns True if the word is alphanumeric sequence 
    of length equal to the given size """
    return re.match(alphanum(size), word)

def isSetX(word, size):
    """ Given a word and a size value, Returns True if the word belongs to set x 
    with a length less or equal to the given size """
    return re.match(fsetx(size), word)

def fsety(size):
    set_y = re.compile(
        r'^[A-Z0-9\?:(,\.)\'\+/\-=!"%&\*<>;]' + "{1,%s}$" % (size))
    return set_y

def fsetz(size):
    set_z = re.compile(
        r'^[A-Za-z0-9\?:(,\.)\'\+/\-=!"%&\*<>;{@#_]' + "{1,%s}$" % (size))
    return set_z

### Auxiliar functions ###
isEOF = lambda lines: len(lines) == 0


def readPageNumberIndicator(lines):
    """ Reading number of pages containing the message """
    (num_line, field) = lines[0]
    m = re.match('^(%s)(%s)\/(%s)$' %
                 (tagp, num(5), alphanumFixed(4)), field)
    if m is not None:
        if m.group(1) != ':28E:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':28E:'))
        elif m.group(3) not in ['LAST', 'MORE', 'ONLY']:
            raise ParsingException(buildErrMsg(
                3, num_line, value='\'LAST\', \'MORE\' or \'ONLY\''))
        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readStatementNumber(lines):
    """ Statement number parsing """
    (num_line, field) = lines[0]
    if ":13A:" in field or ":13J:" in field:  # optional field
        m = re.match('^(%s):STAT\/\/(\d+)$' % (tagp), field)
        if m.group(1) == ':13A:':
            if len(m.group(2)) == 3:
                lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(0, num_line))
        elif m.group(1) == ':13J:':
            if len(m.group(2)) == 5:
                lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(0, num_line))
        else:
            raise ParsingException(buildErrMsg(0, num_line))

def readSEME(lines):
    """ Read Message's sender Reference """
    FIELD_NAME = "Sender's Message Reference"
    (num_line, field) = lines[0]
    m = re.match('^(%s):(%s)\/\/(.*)$' % (tagp, fsetalphanum), field)
    if m is not None:
        if m.group(1) != ':20C:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':20C:'))
        elif m.group(2) != 'SEME':
            raise ParsingException(buildErrMsg(
                4, num_line, field_name=FIELD_NAME, value='\'SEME\''))
        elif re.match(fsetx(16), m.group(3)) is None:
            raise ParsingException(buildErrMsg(5, num_line))
        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readMessageFunction(lines):
    """ Read Function of the Message """
    FIELD_NAME = "Function of the Message"
    (num_line, field) = lines[0]
    m = re.match('^(%s)(?P<function>%s)(\/(?P<subfunction>%s))?$' %
                 (tagp, fsetalphanum, fsetalphanum), field)
    if m is not None:
        if m.group(1) != ':23G:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':23G:'))
        elif m.group('function') not in ['CANC', 'NEWM']:
            raise ParsingException(buildErrMsg(
                4, num_line, field_name=FIELD_NAME, value='\'CANC\',\'NEWM\''))
        elif not m.group('subfunction') is None and m.group('subfunction') not in ['CODU', 'COPY', 'DUPL']:
            raise ParsingException(buildErrMsg(
                6, num_line, subfield_name="subfunction", value='\'CODU\',\'COPY\',\'DUPL\''))
        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readPreparationDateTime(lines):
    """ Read Preparation of the message """
    FIELD_NAME = "Preparation Date/Time"
    (num_line, field) = lines[0]
    if ":98A:" in field or ":98C:" in field or ":98E:" in field:  # optional field
        m = re.match('^(%s):(%s)\/\/(.*)$' % (tagp, fsetalphanum), field)
        if m is not None:
            if(m.group(2) != 'PREP'):
                raise ParsingException(buildErrMsg(
                    4, num_line, value='\'PREP\''))
            if(m.group(1) == ":98A:"):  # Checking format A
                m = re.match('^%s$' % (fdate),  m.group(3))
                if m is not None:
                    if not isCorrectDate(m.group(0)):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="date", pattern="YYYYMMDD"))
                    else:
                        lines.pop(0)
                else:
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="A", pattern=":4!c//8!n"))
            elif(m.group(1) == ":98C:"):  # Checking format C
                m = re.match('^%s%s$' % (fdate, ftime),  m.group(3))
                if m is not None:
                    if not isCorrectDate(m.group(0)):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="date", pattern="YYYYMMDD"))
                    elif not isCorrectTime(m.group('time')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="time", pattern="HHMMSS"))
                    else:
                        lines.pop(0)
                else:
                    raise ParsingException(buildErrMsg(7, num_line,
                                                       field_name=FIELD_NAME, option="C", pattern=":4!c//8!n6!n"))
            elif(m.group(1) == ":98E:"):  # Checking format E
                m = re.match('^%s%s%s$' %
                             (fdate, ftime, fdecimalutc),  m.group(3))
                if m is not None:
                    if not isCorrectDate(m.group(0)):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="date", pattern="YYYYMMDD"))
                    elif not isCorrectTime(m.group('time')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="time", pattern="HHMMSS"))
                    elif not isCorrectUTC(m.group('sign'), m.group('utch'), m.group('utcm')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="UTC", pattern="[N]HH[MM]"))
                    else:
                        lines.pop(0)
                else:
                    raise ParsingException(buildErrMsg(7, num_line,
                                                       field_name=FIELD_NAME, option="E", pattern=":4!c//8!n6!n[,3n][/[N]2!n[2!n]]"))
        else:
            raise ParsingException(buildErrMsg(0, num_line))

def readStatementPeriod(lines):
    """ Read Preparation of the message """
    FIELD_NAME = "Statement Period"
    (num_line, field) = lines[0]
    m = re.match('^(%s):(%s)\/\/(.*)$' % (tagp, fsetalphanum), field)
    if m is not None:
        if m.group(2) != 'STAT':
            raise ParsingException(buildErrMsg(
                4, num_line, value='\'STAT\''))
        if m.group(1) == ':69A:':  # Checking Option A format
            m = re.match('^(%s)\/(%s)$' % (fdate, fdate1),  m.group(3))
            if m is not None:
                if not (isCorrectDate(m.group('date')) and isCorrectDate(m.group('date1'))):
                    raise ParsingException(buildErrMsg(8, num_line,
                                                       field_name=FIELD_NAME, subfield_name="date",
                                                       pattern="YYYYMMDD"))
                else:
                    lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(
                    7, num_line, field_name=FIELD_NAME, option="A", pattern=":4!c//8!n/8!n"))

        elif m.group(1) == ':69B:':  # Checking Option B format
            m = re.match('^(%s)(%s)\/(%s)(%s)$' %
                         (fdate, ftime, fdate1, ftime1),  m.group(3))
            if m is not None:
                if not (isCorrectDate(m.group('date')) and isCorrectDate(m.group('date1'))):
                    raise ParsingException(buildErrMsg(8, num_line,
                                                       field_name=FIELD_NAME, subfield_name="date",
                                                       pattern="YYYYMMDD"))
                elif not (isCorrectTime(m.group('time')) and isCorrectTime(m.group('time1'))):
                    raise ParsingException(buildErrMsg(8, num_line,
                                                       field_name=FIELD_NAME, subfield_name="time",
                                                       pattern="HHMMSS"))
                else:
                    lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(
                    7, num_line, field_name=FIELD_NAME, option="B", pattern="	:4!c//8!n6!n/8!n6!n"))

        else:
            raise ParsingException(buildErrMsg(1, num_line, tag=':69a:'))
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readIndicator1(lines):
    """ Read Function of the Message """
    FIELD_NAME = "Indicator"
    (num_line, field) = lines[0]
    PATTERN = ("^(?P<tag>%s):(?P<qualifier>%s)/"
               "(?P<dss>%s)?/(?P<indicator>%s)$") % (tagp, fsetalphanum, fsetalphanum, fsetalphanum)
    m = re.match(PATTERN, field)
    if m is not None:
        (tag, qualifier, dss, indicator) = (m.group('tag'), m.group('qualifier'), m.group('dss'),
                                            m.group('indicator'))

        if qualifier not in ['SFRE', 'CODE', 'STBA']:  # Check qualifiers
            raise ParsingException(buildErrMsg(4, num_line, field_name=FIELD_NAME,
                                               value="'CODE','SFRE','STBA'"))

        if tag == ':22F:':
            if qualifier == 'SFRE':  # optional
                indicator_values = ['ADHO', 'DAIL',
                                    'INDA', 'MNTH', 'WEEK', 'YEAR']
                if dss is None and indicator not in indicator_values:
                    raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                else:
                    # advance the line until mandatory 22F field with qualifier
                    # STBA
                    lines.pop(0)
                    (num_line, field) = lines[0]
                    if '22F' in field:
                        m = re.match(PATTERN, field)
                        (tag, qualifier, dss, indicator) = (m.group('tag'), m.group('qualifier'), m.group('dss'),
                                                            m.group('indicator'))
                    else:
                        raise ParsingException(buildErrMsg(10, num_line, field_name=FIELD_NAME,
                                                           qualifier_value='STBA'))

            if qualifier == 'CODE':  # optional
                indicator_values = ['COMP', 'DELT']
                if dss is None and indicator not in indicator_values:
                    raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                else:
                    # advance the line until mandatory 22F field with qualifier
                    # STBA
                    lines.pop(0)
                    (num_line, field) = lines[0]
                    if '22F' in field:
                        m = re.match(PATTERN, field)
                        (tag, qualifier, dss, indicator) = (m.group('tag'), m.group('qualifier'), m.group('dss'),
                                                            m.group('indicator'))
                    else:
                        raise ParsingException(buildErrMsg(10, num_line, field_name=FIELD_NAME,
                                                           qualifier_value='STBA'))

            if qualifier == 'STBA':  # This field with this qualifier is mandatory
                indicator_values = ['SETT', 'TRAD']
                if dss is None and indicator not in indicator_values:
                    raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                else:
                    lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(10, num_line, field_name=FIELD_NAME,
                                                   qualifier_value='STBA'))

        else:
            raise ParsingException(buildErrMsg(1, num_line, tag=':22F:'))

    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readLinkedMessage(lines):
    """ Read Linked Message """
    FIELD_NAME = "Linked Message"
    (num_line, field) = lines[0]
    PATTERN = ("^:(?P<qualifier>%s)/"
               "(?P<dss>%s)?/(?P<cod>.*)$") % (fsetalphanum, fsetalphanum)
    TAG_NUMBER = '13'
    OPTIONS = {'A':':4!c//3!c',
               'B': ':4!c/[8c]/30x'}
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS.keys()))

    m = re.match('^(?P<tag>%s)(?P<rest>:?.+)$'% (tagp), field) # check if the tag is valid
    if m:
        tag, tag_num, opt, rest  = m.group('tag'), m.group('tag')[1:3], m.group('tag')[3], m.group('rest') 
        if tag_num == TAG_NUMBER:
            if opt in OPTIONS.keys():
                m1 = re.match(PATTERN, rest)
                if m1 is not None:
                    (qualifier, dss, cod) = (m1.group('qualifier'), m1.group('dss'),
                                                  m1.group('cod'))
                    if qualifier != "LINK":  # check qualifier format
                        raise ParsingException(
                            buildErrMsg(4, num_line, value="'LINK'"))
                    else:

                        if tag == ":13A:":  # checking option A format
                            if not dss is None or not isalphanumStrict(cod, 3) is None:
                                raise ParsingException(buildErrMsg(7, num_line,
                                                                   field_name=FIELD_NAME, option=opt, pattern=OPTIONS[opt]))
                            else:
                                lines.pop(0)
                        elif tag == ":13B:":  # parse option B
                            if ((not dss is None and isalphanum(dss, 8) is None) or
                                    isSetX(cod, 30) is None):
                                raise ParsingException(buildErrMsg(7, num_line,
                                                                   field_name=FIELD_NAME,option=opt, pattern=OPTIONS[opt]))
                            else:
                                lines.pop(0)
                        else:
                            raise ParsingException(buildErrMsg(11, num_line, tag=', '.join([':13A:', ':13B:'])))
                else:
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option=opt, pattern=OPTIONS[opt]))
            else: 
                # invalid option
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            pass # optional Field
    else:
        raise ParsingException(buildErrMsg(0, num_line))


def readReferenceA1(lines):
    """ Read Reference of Link """
    FIELD_NAME = "Reference Link"
    (num_line, field) = lines[0]
    PATTERN = ("^(?P<tag>%s):(?P<qualifier>%s)/"
               "/(?P<ref>.*)$") % (tagp, fsetalphanum)
    m = re.match(PATTERN, field)
    if m is not None:
        (tag, qualifier, ref) = (m.group('tag'),
                                 m.group('qualifier'), m.group('ref'))
        if tag == ":20C:":
            if qualifier in ['PREV', 'RELA']:
                if isSetX(ref, 16):
                    lines.pop(0)
                else:
                    raise ParsingException(buildErrMsg(5, num_line))
            else:
                raise ParsingException(buildErrMsg(4, num_line,
                                                   field_name=FIELD_NAME, value="'PREV', 'RELA'"))
        else:
            raise ParsingException(buildErrMsg(1, num_line, tag=':20C:'))
    else:
        raise ParsingException(buildErrMsg(0, num_line))



def readAccountOwner(lines):
    """ Read the number of the Owner's Account (Optional Field)"""
    FIELD_NAME = "Party: Account Number"
    (num_line, field) = lines[0]
    if ":95P:" in field:  # option P
        m = re.match('^(%s):ACOW\/\/(?P<code>%s)$' % (tagp, fbic), field)
        if not m is None:
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="P", pattern=":ACOW//4!a2!a2!c[3!c]"))
    elif ":95R:" in field:  # option R
        m = re.match('^(%s):ACOW\/(?P<dss>%s)\/(?P<code>%s)$' % (tagp, alphanum(8),
                                                                 fsetx(34)), field)
        if not m is None:
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="R", pattern=":ACOW/8c/34x"))
    else:
        pass  # optional field, let it go

def readSafeAccount(lines):
    """ Read the number of the Safekeeping Acoount (Mandatory Field) """
    FIELD_NAME = "Account: Safekeeping Account"
    (num_line, field) = lines[0]
    if ":97A:" in field[0:5]:  # option P
        m = re.match('^(%s):SAFE\/\/(?P<code>%s)$' %
                     (tagp, fsetx(35)), field)
        if not m is None:
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="A", pattern=":SAFE//35x"))
    elif ":97B:" in field[0:5]:  # option R
        m = re.match('^(%s):SAFE\/(?P<dss>%s)?\/(?P<type>%s)\/(?P<code>%s)$' % (tagp, alphanum(8),
                                                                                alphanumFixed(4), fsetx(35)), field)
        if not m is None:
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="B", pattern=":SAFE/[8c]/4!c/35x"))
    else:
        raise ParsingException(buildErrMsg(1, num_line, tag=':97a:'))

def readFlagsBlockA(lines):
    """ Read Block A Flags (Mandatory Field) """
    FIELD_NAME = "Flag"
    # get ACTI flag first
    (num_line, field) = lines[0]
    m = re.match('^(?P<tag>%s):ACTI\/\/(?P<flag>%s)$' %
                 (tagp, alphaFixed(1)), field)

    if not m is None:
        if m.group('tag') != ':17B:':  # check tag code
            raise ParsingException(buildErrMsg(1, num_line, tag=':17B:'))
        elif m.group('flag') not in ['Y', 'N']:
            raise ParsingException(buildErrMsg(6, num_line,
                                               subfield_name="flag", value="Y or N"))
        lines.pop(0)
        # now get CONS flag
        (num_line, field) = lines[0]
        m = re.match('^(?P<tag>%s):CONS\/\/(?P<flag>%s)$'%
                     (tagp, alphaFixed(1)), field)
        if not m is None:
            if m.group('tag') != ':17B:':  # check tag code
                raise ParsingException(
                    buildErrMsg(1, num_line, tag=':17B:'))
            elif m.group('flag') not in ['Y', 'N']:
                raise ParsingException(buildErrMsg(6, num_line,
                                                   subfield_name="flag", value="Y, N"))
            else:
                lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(10, num_line,
                                               field_name=FIELD_NAME, qualifier_value="CONS"))
    else:
        raise ParsingException(buildErrMsg(10, num_line,
                                           field_name=FIELD_NAME, qualifier_value="ACTI"))



def readStartOfBlock(lines, code):
    """ Start of block B """
    (num_line, field) = lines[0]
    m = re.match('^(%s)(%s)$' % (tagp, alphanum(16)), field)
    if m is not None:
        if m.group(1) != ':16R:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':16R:'+code))
        elif m.group(2) != code:
            raise ParsingException(buildErrMsg(2, num_line, value=code))

        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))


def readSafeAccountBlockB(lines):
    """ Read the number of the Safekeeping Acoount (Conditional Field) """
    FIELD_NAME = "Account: Safekeeping Account"
    (num_line, field) = lines[0]
    if ":97A:" in field[0:5]:  # option P
        m = re.match('^(%s):SAFE\/\/(?P<code>%s)$' %
                     (tagp, fsetx(35)), field)
        if not m is None:
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="A", pattern=":SAFE//35x"))
    elif ":97B:" in field[0:5]:  # option R
        m = re.match('^(%s):SAFE\/(?P<dss>%s)?\/(?P<type>%s)\/(?P<code>%s)$' % (tagp, alphanum(8),
                                                                                alphanumFixed(4), fsetx(35)), field)
        if not m is None:
            if m.group('dss') is None:
                TYPE_CODES = ['ABDR', 'CEND', 'DVPA', 'MARG', 'PHYS', 'SHOR']
                if m.group('type') not in TYPE_CODES:
                    raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value='SAFE', subfield_name="Account Type Code",
                                                       subfield_value=",".join(TYPE_CODES)))
            # All good
            lines.pop(0)
        else:
            raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="B", pattern=":SAFE/[8c]/4!c/35x"))
    else:
        # HEY! CHECK FOR NETWORK RULE C7
        pass

def readPlaceOfSafekeeping(lines):
    """ Read the place of the Safekeeping entity (Optional Field) """
    FIELD_NAME = "Place of Safekeeping"
    (num_line, field) = lines[0]
    m = re.match('^(?P<tag>%s):(?P<rest>.*)$'%(tagp), field)
    if not m is None:
        # define formats for each option
        OPT_B = '(?P<qualifier>%s)\/(?P<dss>%s)?\/(?P<place>%s)(\/(?P<nar>%s))?'%(alphanumFixed(4), alphanum(8), alphanumFixed(4), fsetx(30))
        OPT_C = '(?P<qualifier>%s)\/\/(?P<country>%s)'%(alphanumFixed(4), alphaFixed(2))
        OPT_F = '(?P<qualifier>%s)\/\/(?P<place>%s)\/(?P<bic>%s)'%(alphanumFixed(4), alphanumFixed(4), fbic)
        tag, field = m.group('tag'), m.group('rest')
        if '94B' in tag:
            m = re.match(OPT_B, field)
            if not m is None:
                qualifier, dss, place = m.group('qualifier'), m.group('dss'), m.group('place')
                if qualifier == 'SAFE':
                    if dss is None and place != 'SHHE':
                        raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="Place Code",
                                                       subfield_value='SHHE'))
                    else: # all good
                        lines.pop(0)
                else:
                     raise ParsingException(buildErrMsg(4, num_line, field_name=FIELD_NAME,
                                               value="'SAFE'"))

            else:
                raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="B", pattern=":SAFE/[8c]/4!c[/30x]"))

        elif '94C' in tag:
            m = re.match(OPT_C, field)
            if not m is None:
                qualifier = m.group('qualifier')
                if qualifier == 'SAFE':
                    lines.pop(0) # all good
                else:
                     raise ParsingException(buildErrMsg(4, num_line, field_name=FIELD_NAME,
                                               value="'SAFE'"))

            else:
                raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="C", pattern="SAFE//2!a"))

        elif '94F' in tag:
            m = re.match(OPT_F, field)
            if not m is None:
                qualifier, place = m.group('qualifier'), m.group('place')
                if qualifier == 'SAFE':
                    PLACE_VALUES = ['CUST', 'ICSD', 'NCSD', 'SHHE']
                    if place in PLACE_VALUES:
                        lines.pop(0) # all good
                    else:
                        raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="Place Code",
                                                       subfield_value=",".join(PLACE_VALUES)))

                else:
                     raise ParsingException(buildErrMsg(4, num_line, field_name=FIELD_NAME,
                                               value="'SAFE'"))

            else:
                raise ParsingException(buildErrMsg(7, num_line,
                                               field_name=FIELD_NAME, option="F", pattern="SAFE//4!c/4!a2!a2!c[3!c]"))

        else:
            pass    # optional field


    pass

def readActivityFlag(lines):
    """ Read Block B Activity Flags (Conditional Field) """
    FIELD_NAME = "Acticity Flag"
    # get ACTI flag first
    (num_line, field) = lines[0]
    m = re.match('^(?P<tag>%s):ACTI\/\/(?P<flag>%s)$' % (tagp, alphaFixed(1)), field)
    if not m is None:
        if m.group('tag') != ':17B:':  # check tag code
            raise ParsingException(buildErrMsg(1, num_line, tag=':17B:'))
        elif m.group('flag') not in ['Y', 'N']:
            raise ParsingException(buildErrMsg(6, num_line,
                                               subfield_name="flag", value="Y or N"))
        lines.pop(0)
        # now get CONS flag
    else:
        pass # Optional field



def readEndOfBlock(lines, code):
    """ End of block B """
    (num_line, field) = lines[0]
    m = re.match('^(%s)(%s)$' % (tagp, alphanum(16)), field)
    if m is not None:
        if m.group(1) != ':16S:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':16S:'+code))
        elif m.group(2) != code:
            raise ParsingException(buildErrMsg(2, num_line, value=code))

        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readISIN(lines):
    """ Read Block B Activity Flags (Conditional Field) """
    FIELD_NAME = "Identification of the Financial Instrument"
    OPT_B = '^(?P<tag>%s)(?P<rest>.+)$'%(tagp)
    (num_line, field) = lines[0]
    m = re.match(OPT_B, field)
    if m is not None:
        tag, rest = m.group('tag'), m.group('rest')
        isISINPresent, isDescriptionPresent = False, False
        if tag == ':35B:':
            m = re.match('^ISIN(?P<idisin>.+$)', rest)
            if not m is None: # check ISIN Code (if exists)
                isISINPresent = True
                idisin = m.group('idisin')
                m1 = re.match('^\s%s$'%alphanumFixed(12), idisin)
                if m1:
                    lines.pop(0)
                    (num_line, field) = lines[0]
                else:
                    raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="ISIN", pattern="[ISIN1!e12!c][4*35x]"))

                


            if not isSwiftFieldFormatValid(rest) and isSetX(rest, 35): # Check for description (if exists)
                isDescriptionPresent = True
                lines.pop(0)
                (num_line, field) = lines[0]
                if not isSwiftFieldFormatValid(field) and isSetX(rest, 35):
                    lines.pop(0)
                    (num_line, field) = lines[0]
                    if not isSwiftFieldFormatValid(field) and isSetX(rest, 35):
                        lines.pop(0)
                        (num_line, field) = lines[0]
                        if not isSwiftFieldFormatValid(field) and isSetX(rest, 35):
                            lines.pop(0)

            if not isISINPresent and not isDescriptionPresent:
                raise ParsingException(buildErrMsg(7, num_line, 
                                                   field_name=FIELD_NAME, option="B", pattern="[ISIN1!e12!c][4*35x]"))

        else: # wrong tag code
            raise ParsingException(buildErrMsg(1, num_line, tag=':35B:'))


    else: # not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))



def readPrice(lines):
    """ Read the price of the financial instrument (Optional Field)"""
    (num_line, field) = lines[0]
    TAG_NUMBER = '90'
    OPTIONS = ['A', 'B']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s):(.+)$'% (tagp), field)
    if m:
        tag_num, opt  = m.group('tag')[1:3], m.group('tag')[3]
        if tag_num == TAG_NUMBER:
            if opt in OPTIONS:
                lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            pass # optional Field
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))

def readPriceSource(lines):
    """ Read the source of the price of the Financial instrument (Optional Field)"""
    (num_line, field) = lines[0]
    TAG_NUMBER = '94'
    OPTIONS = ['B']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s)(:)?(.+)$'% (tagp), field)
    if m:
        tag_num, opt  = m.group('tag')[1:3], m.group('tag')[3]
        if tag_num == TAG_NUMBER:
            if opt in OPTIONS:
                lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            pass # optional Field
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))

def readPriceQuotationDate(lines):
    (num_line, field) = lines[0]
    TAG_NUMBER = '98'
    OPTIONS = ['A', 'B']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s)(:)?(.+)$'% (tagp), field)
    if m:
        tag_num, opt  = m.group('tag')[1:3], m.group('tag')[3]
        if tag_num == TAG_NUMBER:
            if opt in OPTIONS:
                lines.pop(0)
            else:
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            pass # optional Field
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))


def readBalance(lines):
    """ Read Balance (Optional Field)"""
    (num_line, field) = lines[0]
    FIELD_NAME = "Balance"
    TAG_NUMBER = '93'
    OPTIONS = ['B']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s)(?P<rest>:?.+)$'% (tagp), field)
    if m: 
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest') 
        if tag_num == TAG_NUMBER:
            if opt in OPTIONS:
                regex = "^:(?P<qualifier>%s)/(?P<dss>%s)?/(?P<type>%s)/(?P<sign>N)?%s$"%(alphanumFixed(4), 
                    alphanum(8), alphanumFixed(4), decimal(15))
                m1 = re.match(regex, rest)
                if m1: # check field format
                    qualifier, dss, typ = m1.group('qualifier'), m1.group('dss'), m1.group('type') 
                    if qualifier in ['FIOP', 'INOP', 'FICL', 'INCL']: # check qualifier
                        if not dss and not typ in ['AMOR', 'FAMT', 'UNIT']: # check quantity type code
                            raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="Quantity Type Code",
                                                       subfield_value=",".join(['AMOR', 'FAMT', 'UNIT'])))
                        else: # all ok
                            lines.pop(0)
                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(['FIOP', 'INOP', 'FICL', 'INCL'])))
                else:
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="B", pattern=":4!c/[8c]/4!c/[N]15d"))


            else:
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            pass # optional Field
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))

def readQuantityFI(lines):
    """ Read Quantity of Financial Instrument (Mandatory Field) """
    (num_line, field) = lines[0]
    FIELD_NAME = "Quantity of Financial Instrument: Posting Quantity"
    TAG_NUMBER = '36'
    OPTIONS = ['B']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    # catch tag and the rest of field
    m = re.match('^(?P<tag>%s):(?P<rest>.+)$'% (tagp), field)
    if m:
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest')
        if tag_num == TAG_NUMBER: # check field tag
            if opt in OPTIONS: # check field option
                regex = r"^(?P<qualifier>%s)//(?P<type>%s)/(?P<quantity>%s)$"%(alphanumFixed(4), alphanumFixed(4), decimal(15))
                m1 = re.match(regex, rest)
                if m1:
                    qualifier, dss, typ = m1.group('qualifier'), m1.group('type'), m1.group('type')
                    if qualifier == 'PSTA': # check qualifier
                        if dss in ['AMOR', 'FAMT', 'UNIT']:
                            lines.pop(0) # all ok
                        else:
                            raise ParsingException(buildErrMsg(9, num_line, field_name=FIELD_NAME,
                                                       qualifier_value=qualifier, subfield_name="Quantity Type Code",
                                                       subfield_value=",".join(['AMOR', 'FAMT', 'UNIT'])))

                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value="PSTA"))
                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="B", pattern=":4!c//4!c/15d"))

            else: # not a valid option for this field
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))

        else: # wrong tag code, mandatory
            raise ParsingException(buildErrMsg(1, num_line, tag=':36B:'))

    else: #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))

def readIndicator2(lines):
    """ Read Transaction Details Indicator  (Mandatory Field)"""
    (num_line, field) = lines[0]
    FIELD_NAME = "Indicator"
    TAG_NUMBER = '22'
    OPTIONS = ['F', 'H']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s):(?P<rest>.+)$'% (tagp), field)
    if m: 
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest') 
        if tag_num == TAG_NUMBER:
            
            if opt == 'F':
                regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<indicator>%s)$"%(alphanumFixed(4), 
                    alphanum(8), alphanumFixed(4))                
                m1 = re.match(regex, rest)
                if m1:
                    lines.pop(0) # all ok

                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="F", pattern=":4!c/[8c]/4!c"))

            elif opt == 'H':

                regex = "^(?P<qualifier>%s)//(?P<indicator>%s)$"%(alphanumFixed(4),alphanumFixed(4))
                m1 = re.match(regex, rest)
                if m1: # check field format
                    lines.pop(0) # all ok

                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="H", pattern=":4!c//4!c"))


            else: # not a valid option for this field
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            # wrong tag code, mandatory
            raise ParsingException(buildErrMsg(1, num_line, tag=':22a:'))
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))


def readTransactionDetailsDate(lines):
    """ Read Transaction Details Indicator  (Mandatory Field)"""
    (num_line, field) = lines[0]
    FIELD_NAME = "Transaction Detail Date"
    TAG_NUMBER = '98'
    OPTIONS = ['A', 'B', 'C']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s):(?P<rest>.+)$'% (tagp), field)
    if m: 
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest') 
        if tag_num == TAG_NUMBER:
            
            if opt == 'A':
                regex = "^(?P<qualifier>%s)//%s$"%(alphanumFixed(4), fdate)                
                m1 = re.match(regex, rest)

                if m1:
                    if not isCorrectDate(m1.group('date')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                            field_name=FIELD_NAME, subfield_name="date",
                                                            pattern="YYYYMMDD"))
                    else:

                        lines.pop(0) # all ok

                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="A", pattern=":4!c//8!n"))

            elif opt == 'B':
                regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<code>%s)$"%(alphanumFixed(4),alphanum(8), alphanumFixed(4))
                m1 = re.match(regex, rest)
                if m1: # check field format

                    lines.pop(0) # all ok

                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="H", pattern=":4!c/[8c]/4!c"))

            elif opt == 'C':
                regex = "^(?P<qualifier>%s)//%s%s$"%(alphanumFixed(4), fdate, ftime)                
                m1 = re.match(regex, rest)
                if m1:
                    if not isCorrectDate(m1.group('date')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                            field_name=FIELD_NAME, subfield_name="date",
                                                            pattern="YYYYMMDD"))
                    elif not isCorrectTime(m1.group('time')):
                        raise ParsingException(buildErrMsg(8, num_line,
                                                           field_name=FIELD_NAME, subfield_name="time", pattern="HHMMSS"))
                    lines.pop(0) # all ok

                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="C", pattern=":4!c//8!n6!n"))


            else: # not a valid option for this field
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            # wrong tag code, mandatory
            raise ParsingException(buildErrMsg(1, num_line, tag=':98a:'))
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))

def readTransactionDetailsParty(lines):
    """ Read Transaction Details Party  (Mandatory Field)"""
    (num_line, field) = lines[0]
    FIELD_NAME = "Party"
    TAG_NUMBER = '95'
    OPTIONS = ['C', 'P', 'Q', 'R']
    QUALIFIERS = ['BUYR', 'DEAG', 'DECU', 'DEI1', 'DEI2', 'PSET', 'REAG', 'RECU', 'REI1', 'REI2', 'SELL']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    m = re.match('^(?P<tag>%s):(?P<rest>.+)$'% (tagp), field)
    if m: 
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest') 
        if tag_num == TAG_NUMBER:        
            if opt == 'C':
                regex = "^(?P<qualifier>%s)//%s$"%(alphanumFixed(4), alphaFixed(2))                
                m1 = re.match(regex, rest)
                if m1:

                    qualifier =  m1.group('qualifier')
                    if qualifier in QUALIFIERS:
                        lines.pop(0) # all ok
                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(QUALIFIERS)))


                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="C", pattern=":4!c//2!a"))
            elif opt == 'P':
                regex = "^(?P<qualifier>%s)//%s$"%(alphanumFixed(4), fbic)                
                m1 = re.match(regex, rest)
                if m1:
                    qualifier =  m1.group('qualifier')
                    if qualifier in QUALIFIERS:
                        lines.pop(0) # all ok
                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(QUALIFIERS)))
                   
                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="P", pattern=":4!c//4!a2!a2!c[3!c]"))

            elif opt == 'R':
                regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<code>%s)$"%(alphanumFixed(4),alphanum(8), fsetx(34))
                m1 = re.match(regex, rest)
                if m1: # check field format
                    qualifier =  m1.group('qualifier')
                    if qualifier in QUALIFIERS:
                        lines.pop(0) # all ok
                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(QUALIFIERS)))
                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="R", pattern=":4!c/[8c]/4!c"))

            elif opt == 'Q':
                regex = "^(?P<qualifier>%s)//(?P<address>%s)$"%(alphanumFixed(4), fsetx(35))                
                m1 = re.match(regex, rest)
                if m1:
                    qualifier, address =  m1.group('qualifier'), m1.group('address'),
                    if qualifier not in QUALIFIERS:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(QUALIFIERS)))
                    # parse address
                    if not isSwiftFieldFormatValid(address):
                        lines.pop(0) 
                        (num_line, field) = lines[0]
                        if not isSwiftFieldFormatValid(field) and isSetX(field, 35):

                            lines.pop(0)
                            (num_line, field) = lines[0]
                            if not isSwiftFieldFormatValid(field) and isSetX(field, 35):
                                lines.pop(0)
                                (num_line, field) = lines[0]
                                if not isSwiftFieldFormatValid(field) and isSetX(field, 35):
                                    lines.pop(0)
                    else:
                        raise ParsingException(buildErrMsg(7, num_line,
                                                       field_name=FIELD_NAME, option="Q", pattern=":4!c//4*35x"))


                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="Q", pattern=":4!c//4*35x6!n"))


            else: # not a valid option for this field
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))
        else:
            # wrong tag code, mandatory
            raise ParsingException(buildErrMsg(1, num_line, tag=':98a:'))
            
    else:  #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))


def readPartyReference(lines):
    """ Read Message's sender Reference """
    FIELD_NAME = "Processing Reference"
    (num_line, field) = lines[0]
    m = re.match('^(%s):(%s)\/\/(.*)$' % (tagp, fsetalphanum), field)
    if m is not None:
        if m.group(1) != ':20C:':
            raise ParsingException(buildErrMsg(1, num_line, tag=':20C:'))
        elif m.group(2) != 'PROC':
            raise ParsingException(buildErrMsg(
                4, num_line, field_name=FIELD_NAME, value='\'PROC\''))
        elif re.match(fsetx(16), m.group(3)) is None:
            raise ParsingException(buildErrMsg(5, num_line))
        lines.pop(0)
    else:
        raise ParsingException(buildErrMsg(0, num_line))

def readAmount(lines):
    """ Amount (Mandatory Field) """
    (num_line, field) = lines[0]
    FIELD_NAME = "Amount"
    TAG_NUMBER = '19'
    OPTIONS = ['A']
    QUALIFIERS = ['PSTA', 'ACRU']
    VALID_TAGS = list(map(lambda x: ':%s%s:'%(TAG_NUMBER, x), OPTIONS))
    # catch tag and the rest of field
    m = re.match('^(?P<tag>%s):(?P<rest>.+)$'% (tagp), field)
    if m:
        tag_num, opt, rest  = m.group('tag')[1:3], m.group('tag')[3], m.group('rest')
        if tag_num == TAG_NUMBER: # check field tag
            if opt in OPTIONS: # check field option
                regex = r"^(?P<qualifier>%s)//(?P<sign>N)?(?P<code>%s)(?P<amount>%s)$"%(alphanumFixed(4), alphaFixed(3), decimal(15))
                m1 = re.match(regex, rest)
                if m1:
                    qualifier, code, amount = m1.group('qualifier'), m1.group('code'), m1.group('amount')
                    if qualifier in QUALIFIERS: # check qualifier
                            lines.pop(0) # all ok

                    else:
                        raise ParsingException(buildErrMsg(4, num_line,
                                                            field_name=FIELD_NAME, value=",".join(QUALIFIERS)))
                else: # subfields format not correct
                    raise ParsingException(buildErrMsg(
                        7, num_line, field_name=FIELD_NAME, option="A", pattern=":4!c//[N]3!a15d"))

            else: # not a valid option for this field
                raise ParsingException(buildErrMsg(11, num_line, tag=', '.join(VALID_TAGS)))

        else: # wrong tag code
            raise ParsingException(buildErrMsg(1, num_line, tag=':19A:'))

    else: #  not a valid swift's field format
        raise ParsingException(buildErrMsg(0, num_line))




def parseBlockA(lines):
    """ Swift's MT536 message BlockA parsing """
    readStartOfBlock(lines, 'GENL')
    readPageNumberIndicator(lines)
    readStatementNumber(lines)
    readSEME(lines)
    readMessageFunction(lines)
    readPreparationDateTime(lines)
    readStatementPeriod(lines)
    readIndicator1(lines)
    readBlocksA1(lines)
    readAccountOwner(lines)
    readSafeAccount(lines)
    readFlagsBlockA(lines)
    readEndOfBlock(lines, 'GENL')

def readBlocksA1(lines):
    (num_line, field) = lines[0]
    while(':16R:LINK' == field):
        lines.pop(0)
        readLinkedMessage(lines)
        readReferenceA1(lines)
        (num_line, field) = lines[0]
        if ':16S:LINK' != field:  # Check for end of block A1
            raise ParsingException(buildErrMsg(0, num_line))
        else:
            lines.pop(0)
            (num_line, field) = lines[0]


def parseBlocksB(lines):
    """ Swift's MT536 message BlocksB parsing """
    while not isEOF(lines) and not re.match(r':16R:SUBSAFE', lines[0][1]) is None :
        parseBlockB(lines)

def parseBlockB(lines):
    """ Swift's MT536 message BlocksB parsing """
    readStartOfBlock(lines, 'SUBSAFE')
    readAccountOwner(lines)
    readSafeAccountBlockB(lines)
    readPlaceOfSafekeeping(lines)
    readActivityFlag(lines)
    parseBlocksB1(lines)
    readEndOfBlock(lines, 'SUBSAFE')

# BLOCKS B1
def parseBlocksB1(lines):
    while not re.match(r':16R:FIN', lines[0][1]) is None :
        parseBlockB1(lines)

def parseBlockB1(lines):
    readStartOfBlock(lines, 'FIN')
    readISIN(lines)
    readPrice(lines)
    readPriceSource(lines)
    readPriceQuotationDate(lines)
    readBalance(lines)
    readBalance(lines)
    parseBlocksB1a(lines)
    readEndOfBlock(lines, 'FIN')

def parseBlocksB1a(lines): # Mandatory Repetitive sequence
    while True:
        readStartOfBlock(lines, 'TRAN')
        parseBlocksB1a1(lines)
        parseBlockB1a2(lines)
        readEndOfBlock(lines, 'TRAN')
        if re.match(r':16R:TRAN', lines[0][1]) is None:
            break

def parseBlocksB1a1(lines):
    while True:
        readStartOfBlock(lines, 'LINK')
        readLinkedMessage(lines)
        readReferenceA1(lines)
        readEndOfBlock(lines, 'LINK')
        if re.match(r':16R:LINK', lines[0][1]) is None:
            break

def parseBlockB1a2(lines):
    """ Parsing Transaction Details Block """
    readStartOfBlock(lines, 'TRANSDET')

    # ignore Place Optional Repetitive Field
    while re.search(r':94[BCFH]:', lines[0][1]): 
        lines.pop(0)
       

    ### Quantity Mandatory repetitive fields
    while True: 
        readQuantityFI(lines)
        if re.search(r':36B:', lines[0][1]) is None:
            break

    # Ignore Number of Days Accrued Field (Optional)
    if re.search(r':99A::DAAC/', lines[0][1]):
        lines.pop(0)

    ### Amount Field(Optional Repetitive)
    if re.search(r':19A::PSTA/', lines[0][1]):
        readAmount(lines)
    if re.search(r':19A::ACRU/', lines[0][1]):
        readAmount(lines)

    ### Indicator repetitive fields (Mandatories)   
    if not re.search(r':22F::TRAN/', lines[0][1]):
        raise ParsingException(buildErrMsg(10, lines[0][0], field_name='Indicator',
                                                           qualifier_value='TRAN'))
    readIndicator2(lines)
    if not re.search(r':22H::REDE/', lines[0][1]):
        raise ParsingException(buildErrMsg(10, lines[0][0], field_name="Indicator",
                                                           qualifier_value='REDE'))
    readIndicator2(lines)
    if not re.search(r':22H::PAYM/', lines[0][1]):
        raise ParsingException(buildErrMsg(10, lines[0][0], field_name="Indicator",
                                                           qualifier_value='PAYM'))
    readIndicator2(lines)
    while re.search(r':22[A-Z]:', lines[0][1]): # mandatory repetitive field
        readIndicator2(lines)

    ### Date time fields (Mandatory Repetitive)
    if not re.search(r':98[A-B]::ESET/', lines[0][1]):
        raise ParsingException(buildErrMsg(10, lines[0][0], field_name='DATE/TIME',
                                            qualifier_value='ESET'))
    readTransactionDetailsDate(lines)

    while re.search(r':98[A-Z]:', lines[0][1]): # mandatory repetitive field
        readTransactionDetailsDate(lines)

    # ignore fields until start of B1a2A block
    # or end of TRANSDET BLOCK
    while True: 
        if re.search(r':16R:SETPRTY', lines[0][1]) or re.search(r':16S:TRANSDET', lines[0][1]):
            break
        lines.pop(0)

    readBlocksB1a2A(lines)
        
    readEndOfBlock(lines, 'TRANSDET')


def readBlocksB1a2A(lines):
    (num_line, field) = lines[0]
    while(':16R:SETPRTY' == field):
        readStartOfBlock(lines, 'SETPRTY')
        readTransactionDetailsParty(lines)
        (num_line, field) = lines[0]
        if re.search(':97[A-Z]:', field): # check if safe account is included
            readSafeAccount(lines)
        (num_line, field) = lines[0]
        if re.search(r':20[A-Z]:', field): # check if reference is included
            readPartyReference(lines)
        readEndOfBlock(lines, 'SETPRTY')
        (num_line, field) = lines[0]

### Execute ###
if __name__ == '__main__':
    PATH = 'in.txt'
    with open(PATH, 'r') as F:
        # get message line by line 
        # enumerate lines so we can have the line numbers too
        MT536 = list(filter(lambda par: len(par[1]) > 1, list(enumerate(F.readlines(), start=1))))
        # stripping the breaklines and empty lines
        MT536 = list(map(lambda x: (x[0], x[1].strip("\n ")), MT536))
    try:
        parseBlockA(MT536)
        parseBlocksB(MT536)
    except ParsingException as error:
        print(error)
    except IndexError:
        print("Error de sintaxis. Fin inesperado del mensaje.")

    print(MT536)
