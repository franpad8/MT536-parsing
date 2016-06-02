""" Parseo de mensaje MT536 de Swift """
import re

# for printing json nicely
import pprint

### Exception Handling Definition ###


class ParsingError(Exception):
    """ Custom Exception Class for Parsing Errors """
    pass

### Build specific format error ###


def _build_err_msg(code, line, language, **kargs):
    if code in [0, 5, 13, 14]:
        msg = (_ERROR_DICT[code][language]) % (line)
    elif code in [1, 11]:
        msg = (_ERROR_DICT[code][language]) % (line, kargs["tag"])
    elif code in [2, 3]:
        msg = (_ERROR_DICT[code][language]) % (line, kargs["value"])
    elif code == 4:
        msg = (_ERROR_DICT[code][language]) % (
            line, kargs["field_name"], kargs["value"])
    elif code == 6:
        msg = (_ERROR_DICT[code][language]) % (
            line, kargs["subfield_name"], kargs["value"])
    elif code == 7:
        msg = (_ERROR_DICT[code][language]) % (line, kargs[
            "field_name"], kargs["option"], kargs["pattern"])
    elif code == 8:
        msg = (_ERROR_DICT[code][language]) % (line, kargs["field_name"], kargs["subfield_name"],
                                               kargs["pattern"])
    elif code == 9:
        msg = (_ERROR_DICT[code][language]) % (line, kargs["field_name"], kargs["qualifier_value"],
                                               kargs["subfield_name"], kargs["subfield_value"])
    elif code == 10:
        msg = (_ERROR_DICT[code][language]) % (
            line, kargs["field_name"], kargs["qualifier_value"])
    elif code == 12:
        msg = (_ERROR_DICT[code][language]) % kargs["isin"]
    else:
        msg = (_ERROR_DICT[0][language]) % (line)
    return msg

### Define dictionary of errors with respective languages ###
_ERROR_DICT = {
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
    12: {
        0: "Error de validación del mensaje. El balance inicial y final no coincide con las transacciones asociadas al Intrumento Financiero de ISIN '%s'.",
        1: "Message Validation Error. Initial and final balance don't match with the transactions movements of the FIN with ISIN '%s'."
    },
    13: {
        0: "Error en la linea %s. La cabecera del mensaje no contiene el formato apropiado.",
        1: "Error at line %s. Message's Header doesn't contain the correct format."
    },
    14: {
        0: "Error en la linea %s. El pie de página del mensaje no contiene el formato apropiado.",
        1: "Error at line %s. Message's Footer doesn't contain the correct format."
    }
}

### Defined REGEXs ###
R_TAG_P = ':[0-9]{2}[A-Z]:'
R_FSET_ALPHANUM = "[A-Z0-9]+"
R_FSET_ALPHA = "[A-Z]+"
R_FSET_X = r"[A-Za-z0-9/-?:(.,)'+]"
R_FSET_BIC = "[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?"
R_FDATE = r'(?P<date>(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2}))'
R_FDATE1 = r'(?P<date1>(?P<year1>\d{4})(?P<month1>\d{2})(?P<day1>\d{2}))'
R_FTIME = r'(?P<time>(?P<hour>\d{2})(?P<min>\d{2})(?P<sec>\d{2}))'
R_FTIME1 = r'(?P<time1>(?P<hour1>\d{2})(?P<min1>\d{2})(?P<sec1>\d{2}))'
R_FDECIMAL_UTC = r'(,(?P<decimals>\d{1,3}))?(/(?P<sign>N)?(?P<utch>\d{2}(?P<utcm>\d{2})?))?'
R_FCORRECT_DATE = r'\d{4}(0[1-9]|1[0-2])([0-2][1-9]|3[0-1])'
R_FCORRECT_TIME = r'([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])'

### Auxiliar functions ###


def alpha(size):
    """ Return REGEX for alphabetic characters
        of length less or equal to size"""
    return "[A-Z]{1,%s}" % size


def alpha_fixed(size):
    """ Return REGEX for alphabetic characters
        of length equal to size"""
    return "[A-Z]{%s}" % size


def alphanum(size):
    """ Return REGEX for alphanumeric characters
        of length less or equal to size"""
    _alphanum = '[A-Z0-9]' + "{1,%s}" % (size)
    return _alphanum


def alphanum_fixed(size):
    """ Return REGEX for alphanumeric characters
    of length equal to size """
    return '[A-Z0-9]{%s}' % (size)


def num(size):
    """ Return a Regex for numbers of length equal or less to a given size """
    return r'\d{1,%s}' % (size)


def decimal(size):
    """ Return a Regex for decimal numbers of length equal or less to a given size """
    return r'\d{1,%s},\d*' % size


def fsetx(size):
    """ Return a Regex for R_FSET_X of length equal or less to a given size """
    return r'((?!.*//.*)(?!/)%s{1,%s}(?<!/))' % (R_FSET_X, size)

def fsetx_free(size):
    """ Return a Regex for R_FSET_X of length equal or less to a given size """
    return r'%s{1,%s}' % (R_FSET_X, size)

### Format Verifications routines ###


def is_correct_date(date):
    """ Verify if a given date is format valid """
    if re.match(R_FCORRECT_DATE, date):
        return True
    return False


def is_correct_time(time):
    """ Verify if a given time is format valid """
    if re.match(R_FCORRECT_TIME, time):
        return True
    return False


def is_correct_utc(sign, utch, utcm):
    """ Verify if a given UTC is format valid """
    if not utch is None and not re.match('[0-1][0-9]|2[0-3]', utch):
        return False
    else:
        if not utcm is None:
            if not re.match('[0-5][0-9]', utcm):
                return False
    return True


def is_swift_field_format_valid(word):
    """ Given a word, determines if it is a valid complete swift field """
    return bool(re.match('%s(.+)' % R_TAG_P, word))


def is_alphanum_strict(word, size):
    """ Given a word and a size value, Returns True if the word is alphanumeric sequence
    of length equal to the given size """
    return re.match(alphanum_fixed(size), word)


def is_alphanum(word, size):
    """ Given a word and a size value, Returns True if the word is alphanumeric sequence
    of length equal to the given size """
    return re.match(alphanum(size), word)


def is_setx(word, size):
    """ Given a word and a size value, Returns True if the word belongs to set x
    with a length less or equal to a given size """
    return re.match(fsetx(size), word)

def is_setx_free(word, size):
    """ Given a word and a size value, Returns True if the word belongs to set x
    with a length less or equal to a given size """
    return re.match(fsetx_free(size), word)

_IS_EOF = lambda lines: len(lines) == 0


class MT536Parser():
    """ Class that encapsulates the MT536 parsing functionality """

    def __init__(self, path, lang=0):
        """ Constructor """
        self._language = lang
        self._path = path

    def parse(self):
        """ Run the parser """
        no_errors = True
        current_page = 0
        # structure where all relevant info of ALL messages found in this file 
        # will be stored 
        list_results = [] 
         # structure where all relevant info of ONE message will be stored
        # build the file path
        with open(self._path, 'r') as _file:
            # get message line by line
            # enumerate lines so we can have the line numbers too
            # stripping the breaklines and empty lines
            _mt536 = [(x[0], x[1].strip("\n ")) for x in list(
                enumerate(_file.readlines(), start=1)) if len(x[1]) > 1]
        try:
            while True:
                result = {}
                self._parse_header(_mt536)
                while True:
                    page = {} # structure where all relevant info of the current page will be stored
                    page.update(self._parse_block_a(_mt536))
                    acti_flag = page['general']['acti']
                    if acti_flag == 'N': # if message without transactions updates during the given period
                        result = page
                        break
                    else:
                        current_page, indicator = page['general']['continuation']['page'], page['general']['continuation']['indicator']
                        page.update(self._parse_blocks_b(_mt536))
                        self._read_blocks_c(_mt536)
                        self._rules_validate(page)
                        if int(current_page) == 1: # if it's the first page then we just copy the structure
                            result = page
                        else: # otherwise, we concatenate transactions with the ones of the pages we already read
                            result['accounts'][0]['financial_instruments'] += page['accounts'][0]['financial_instruments']
                        if indicator in ['LAST', 'ONLY']:
                            break
                continua = self._parse_footer(_mt536)
                list_results.append(result)
                if not continua:
                    break # No mas mensajes en el archivo

        except ParsingError as error:
            no_errors = False
            msg = error.__str__()
        except IndexError:
            no_errors = False
            msg = "Error de sintaxis. Fin inesperado del mensaje."

        if no_errors:
            return (True, list_results)
        else:
            return (False, msg)

        # print("Remaining:\n%s"%_mt536)
        # print("Result:")

    ### Copiar DESDE AQUI al Codigo fuente de Matcher!!!!
    def _rules_validate(self, result):
        # for every Financial Instrument, its final balance must
        # be equal to its inicial balance + sum of transactions movements
        for sub_account in result['accounts']:
            for fin in sub_account['financial_instruments']:
                # asks if balances are available (in MT536 those fields are optional)
                if 'opening_balance' in fin and 'closing_balance' in fin:
                    acc = 0.0
                    for trx in fin['transactions']:
                        if trx['details']['rede'] == 'RECE':
                            acc += trx['details']['quantity_fi'][0]['quantity']
                        else:
                            acc -= trx['details']['quantity_fi'][0]['quantity']
                    if ("%.2f" % (fin['opening_balance']['balance']+acc)) != ("%.2f" % (fin['closing_balance']['balance'])):
                        raise ParsingError(_build_err_msg(12, None, self._language, isin=fin['isin']['code']))


    def _parse_header(self, lines):
        """ Parse message header """
        (num_line, line) = lines[0]
        header_pattern =r"^\{1:[A-Z0-9]{25}\}\{4:(\{\d+:\d+\})+\}\{1:[A-Z0-9]{25}\}\{2:[A-Z0-9]+\}\{4:$"
        if not re.match(header_pattern, line):
            raise ParsingError(_build_err_msg(13, num_line, self._language))
        lines.pop(0)

    def _parse_footer(self, lines):
        (num_line, line) = lines[0]
        # tanto footer como header de un nuevo mensaje me puede llegar en una misma linea
        header_pattern =r"^-\}\{5:(\{%s:%s\})+\}\{S:(\{%s:[A-Z0-9]*\})+\}(?P<cont>\$)?(?P<rest>[^$]*)" % (R_FSET_ALPHA, R_FSET_ALPHANUM, R_FSET_ALPHA)
        mtch = re.match(header_pattern, line)
        if not mtch:
            raise ParsingError(_build_err_msg(14, num_line, self._language))
        if mtch.group('cont'): # si queda al menos otro mensaje en el archivo
            header = (lines[0][0], mtch.group('rest')) # creo una nueva linea con el header
            lines.pop(0) # borro la linea leida
            lines.insert(0, header) # inserto la linea con el header, será leida proximamente
            return True
        else:
            lines.pop(0)
            return False



    def _read_page_number_indicator(self, lines):
        """ Reading number of pages containing the message """
        result = {}
        (num_line, field) = lines[0]
        mtch = re.match(r'^(%s)(%s)/(%s)$' %
                        (R_TAG_P, num(5), alphanum_fixed(4)), field)
        if mtch is not None:
            if mtch.group(1) != ':28E:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':28E:'))
            elif mtch.group(3) not in ['LAST', 'MORE', 'ONLY']:
                raise ParsingError(_build_err_msg(
                    3, num_line, self._language, value='\'LAST\', \'MORE\' or \'ONLY\''))
            result = {"indicator": mtch.group(3), "page": mtch.group(2)}
            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return {"continuation": result}

    def _read_statement_number(self, lines):
        """ Statement number parsing """
        (num_line, field) = lines[0]
        if ":13A:" in field or ":13J:" in field:  # optional field
            mtch = re.match(r'^(%s):STAT//(\d+)$' % (R_TAG_P), field)
            if mtch.group(1) == ':13A:':
                if len(mtch.group(2)) == 3:
                    lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(
                        0, num_line, self._language))
            elif mtch.group(1) == ':13J:':
                if len(mtch.group(2)) == 5:
                    lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(
                        0, num_line, self._language))
            else:
                raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_seme(self, lines):
        """ Read Message's sender Reference """
        result = {}
        field_name = "Sender's Message Reference"
        (num_line, field) = lines[0]
        mtch = re.match(r'^(%s):(%s)//(.*)$' %
                        (R_TAG_P, R_FSET_ALPHANUM), field)
        if mtch is not None:
            if mtch.group(1) != ':20C:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':20C:'))
            elif mtch.group(2) != 'SEME':
                raise ParsingError(_build_err_msg(
                    4, num_line, self._language, field_name=field_name, value='\'SEME\''))
            elif re.match(fsetx(16), mtch.group(3)) is None:
                raise ParsingError(_build_err_msg(5, num_line, self._language))
            # add seme to structure
            result["seme"] = mtch.group(3)
            # all ok, pass line
            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _read_message_function(self, lines):
        """ Read Function of the Message """
        field_name = "Function of the Message"
        (num_line, field) = lines[0]
        mtch = re.match(r'^(%s)(?P<function>%s)(/(?P<subfunction>%s))?$' %
                        (R_TAG_P, R_FSET_ALPHANUM, R_FSET_ALPHANUM), field)
        if mtch is not None:
            if mtch.group(1) != ':23G:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':23G:'))
            elif mtch.group('function') not in ['CANC', 'NEWM']:
                raise ParsingError(_build_err_msg(
                    4, num_line, self._language, field_name=field_name, value='\'CANC\',\'NEWM\''))
            elif not mtch.group('subfunction') is None and mtch.group('subfunction') not in ['CODU', 'COPY', 'DUPL']:
                raise ParsingError(_build_err_msg(6, num_line, self._language,
                                                  subfield_name="subfunction",
                                                  value='\'CODU\',\'COPY\',\'DUPL\''))
            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_preparation_date_time(self, lines):
        """ Read Preparation of the message """
        field_name = "Preparation Date/Time"
        (num_line, field) = lines[0]
        if ":98A:" in field or ":98C:" in field or ":98E:" in field:  # optional field
            mtch = re.match(r'^(%s):(%s)//(.*)$' %
                            (R_TAG_P, R_FSET_ALPHANUM), field)
            if mtch is not None:
                if mtch.group(2) != 'PREP':
                    raise ParsingError(_build_err_msg(
                        4, num_line, self._language, value='\'PREP\''))
                if mtch.group(1) == ":98A:":  # Checking format A
                    mtch = re.match('^%s$' % (R_FDATE), mtch.group(3))
                    if mtch is not None:
                        if not is_correct_date(mtch.group(0)):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="date", pattern="YYYYMMDD"))
                        else:
                            lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="A", pattern=":4!c//8!n"))
                elif mtch.group(1) == ":98C:":  # Checking format C
                    mtch = re.match('^%s%s$' %
                                    (R_FDATE, R_FTIME),  mtch.group(3))
                    if mtch is not None:
                        if not is_correct_date(mtch.group(0)):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="date", pattern="YYYYMMDD"))
                        elif not is_correct_time(mtch.group('time')):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="time", pattern="HHMMSS"))
                        else:
                            lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                       field_name=field_name, option="C", pattern=":4!c//8!n6!n"))
                elif mtch.group(1) == ":98E:":  # Checking format E
                    mtch = re.match('^%s%s%s$' %
                                    (R_FDATE, R_FTIME, R_FDECIMAL_UTC), mtch.group(3))
                    if mtch is not None:
                        if not is_correct_date(mtch.group(0)):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="date", pattern="YYYYMMDD"))
                        elif not is_correct_time(mtch.group('time')):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="time", pattern="HHMMSS"))
                        elif not is_correct_utc(mtch.group('sign'), mtch.group('utch'), mtch.group('utcm')):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="UTC", pattern="[N]HH[MM]"))
                        else:
                            lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                       field_name=field_name, option="E", pattern=":4!c//8!n6!n[,3n][/[N]2!n[2!n]]"))
            else:
                raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_statement_period(self, lines):
        """ Read Preparation of the message """
        result = {}
        field_name = "Statement Period"
        (num_line, field) = lines[0]
        mtch = re.match('^(%s):(%s)\/\/(.*)$' %
                        (R_TAG_P, R_FSET_ALPHANUM), field)
        if mtch is not None:
            if mtch.group(2) != 'STAT':
                raise ParsingError(_build_err_msg(
                    4, num_line, self._language, value='\'STAT\''))
            if mtch.group(1) == ':69A:':  # Checking Option A format
                mtch = re.match(r'^(%s)/(%s)$' %
                                (R_FDATE, R_FDATE1), mtch.group(3))
                if mtch is not None:
                    if not (is_correct_date(mtch.group('date')) and is_correct_date(mtch.group('date1'))):
                        raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                            field_name=field_name, subfield_name="date",
                                                            pattern="YYYYMMDD"))
                    else:
                        # Store dates
                        result["statement_period"] = {"from": mtch.group('date'), "to": mtch.group('date1')}
                        lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                   field_name=field_name, option="A", pattern=":4!c//8!n/8!n"))

            elif mtch.group(1) == ':69B:':  # Checking Option B format
                mtch = re.match(r'^(%s)(%s)/(%s)(%s)$' %
                                (R_FDATE, R_FTIME, R_FDATE1, R_FTIME1), mtch.group(3))
                if mtch is not None:
                    if not (is_correct_date(mtch.group('date')) and is_correct_date(mtch.group('date1'))):
                        raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                       field_name=field_name, subfield_name="date",
                                                       pattern="YYYYMMDD"))
                    elif not (is_correct_time(mtch.group('time')) and is_correct_time(mtch.group('time1'))):
                        raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                    field_name=field_name, subfield_name="time",
                                                    pattern="HHMMSS"))
                    else:
                        # Store dates
                        result["statement_period"] = {"from": mtch.group('date')+mtch.group('time'), "to": mtch.group('date1')+mtch.group('time')}
                        lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(
                        7, num_line, self._language, field_name=field_name, option="B", pattern="	:4!c//8!n6!n/8!n6!n"))

            else:
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':69a:'))
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _read_indicator1(self, lines):
        """ Read Function of the Message """
        result = {}
        field_name = "Indicator"
        (num_line, field) = lines[0]
        pattern = ("^(?P<tag>%s):(?P<qualifier>%s)/"
                   "(?P<dss>%s)?/(?P<indicator>%s)$") % (R_TAG_P, R_FSET_ALPHANUM, R_FSET_ALPHANUM, R_FSET_ALPHANUM)
        mtch = re.match(pattern, field)
        if mtch is not None:
            (tag, qualifier, dss, indicator) = (mtch.group('tag'), mtch.group('qualifier'), mtch.group('dss'),
                                                mtch.group('indicator'))

            if qualifier not in ['SFRE', 'CODE', 'STBA']:  # Check qualifiers
                raise ParsingError(_build_err_msg(4, num_line, self._language, field_name=field_name,
                                               value="'CODE','SFRE','STBA'"))

            if tag == ':22F:':
                if qualifier == 'SFRE':  # optional
                    indicator_values = ['ADHO', 'DAIL',
                                        'INDA', 'MNTH', 'WEEK', 'YEAR']
                    if dss is None and indicator not in indicator_values:
                        raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                    else:
                        
                        # store Frequency
                        result["frequency"] = indicator
                        lines.pop(0)
                        # advance the line until mandatory 22F field with qualifier STBA
                        (num_line, field) = lines[0]
                        if '22F' in field:
                            mtch = re.match(pattern, field)
                            (tag, qualifier, dss, indicator) = (mtch.group('tag'), mtch.group('qualifier'), mtch.group('dss'),
                                                                mtch.group('indicator'))
                        else:
                            raise ParsingError(_build_err_msg(10, num_line, self._language, field_name=field_name,
                                                           qualifier_value='STBA'))

                if qualifier == 'CODE':  # optional
                    indicator_values = ['COMP', 'DELT']
                    if dss is None and indicator not in indicator_values:
                        raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                    else:
                        # advance the line until mandatory 22F field with qualifier
                        # STBA
                        lines.pop(0)
                        (num_line, field) = lines[0]
                        if '22F' in field:
                            mtch = re.match(pattern, field)
                            (tag, qualifier, dss, indicator) = (mtch.group('tag'), mtch.group('qualifier'), mtch.group('dss'),
                                                                mtch.group('indicator'))
                        else:
                            raise ParsingError(_build_err_msg(10, num_line, self._language, field_name=field_name,
                                                           qualifier_value='STBA'))

                if qualifier == 'STBA':  # This field with this qualifier is mandatory
                    indicator_values = ['SETT', 'TRAD']
                    if dss is None and indicator not in indicator_values:
                        raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                       qualifier_value=qualifier, subfield_name="indicator",
                                                       subfield_value=",".join(indicator_values)))
                    else:
                        lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(10, num_line, self._language, field_name=field_name,
                                                   qualifier_value='STBA'))

            else:
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':22F:'))

        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _read_linked_message(self, lines):
        """ Read Linked Message """
        field_name = "Linked Message"
        (num_line, field) = lines[0]
        pattern = ("^:(?P<qualifier>%s)/"
                   "(?P<dss>%s)?/(?P<cod>.*)$") % (R_FSET_ALPHANUM, R_FSET_ALPHANUM)
        tag_number = '13'
        options = {'A': ':4!c//3!c',
                   'B': ':4!c/[8c]/30x'}
        valid_tags = list(map(lambda x: ':%s%s:' %
                              (tag_number, x), options.keys()))

        mtch = re.match('^(?P<tag>%s)(?P<rest>:?.+)$' %
                        (R_TAG_P), field)  # check if the tag is valid
        if mtch:
            tag, tag_num, opt, rest = mtch.group('tag'), mtch.group(
                'tag')[1:3], mtch.group('tag')[3], mtch.group('rest')
            if tag_num == tag_number:
                if opt in options.keys():
                    mtch1 = re.match(pattern, rest)
                    if mtch1 is not None:
                        (qualifier, dss, cod) = (mtch1.group('qualifier'), mtch1.group('dss'),
                                                 mtch1.group('cod'))
                        if qualifier != "LINK":  # check qualifier format
                            raise ParsingError(
                                _build_err_msg(4, num_line, self._language, value="'LINK'"))
                        else:

                            if tag == ":13A:":  # checking option A format
                                if not dss is None or not is_alphanum_strict(cod, 3) is None:
                                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                                   field_name=field_name, option=opt, pattern=options[opt]))
                                else:
                                    lines.pop(0)
                            elif tag == ":13B:":  # parse option B
                                if ((not dss is None and is_alphanum(dss, 8) is None) or
                                        is_setx(cod, 30) is None):
                                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                                   field_name=field_name, option=opt, pattern=options[opt]))
                                else:
                                    lines.pop(0)
                            else:
                                raise ParsingError(_build_err_msg(
                                    11, num_line, self._language, tag=', '.join([':13A:', ':13B:'])))
                    else:
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option=opt, pattern=options[opt]))
                else:
                    # invalid option
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                pass  # optional Field
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_reference_a1(self, lines):
        """ Read Reference of Link """
        result = {}
        field_name = "Reference Link"
        (num_line, field) = lines[0]
        pattern = ("^(?P<tag>%s):(?P<qualifier>%s)/"
                   "/(?P<ref>.*)$") % (R_TAG_P, R_FSET_ALPHANUM)
        mtch = re.match(pattern, field)
        if mtch is not None:
            (tag, qualifier, ref) = (mtch.group('tag'),
                                     mtch.group('qualifier'), mtch.group('ref'))
            if tag == ":20C:":
                if qualifier in ['PREV', 'RELA']:
                    if is_setx(ref, 16):
                        if qualifier == 'RELA':
                            result['rela'] = ref
                        lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(
                            5, num_line, self._language))
                else:
                    raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                   field_name=field_name, value="'PREV', 'RELA'"))
            else:
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':20C:'))
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return result

    def _read_reference_b1a1(self, lines):
        """ Read Reference of Link """
        result = ""
        field_name = "Reference Link"
        (num_line, field) = lines[0]
        pattern = ("^(?P<tag>%s):(?P<qualifier>%s)/"
                   "/(?P<ref>.*)$") % (R_TAG_P, R_FSET_ALPHANUM)
        mtch = re.match(pattern, field)
        if mtch is not None:
            (tag, qualifier, ref) = (mtch.group('tag'),
                                     mtch.group('qualifier'), mtch.group('ref'))
            if tag == ":20C:":
                QUALIFIERS = ['PREV', 'RELA', 'POOL', 'TRRF', 'COMM', 'ASRF', 'CORP', 'TCTR',
                              'CLTR', 'CLCI', 'TRCI', 'MITI', 'PCTI']
                if qualifier in QUALIFIERS:
                    if is_setx(ref, 16):
                        if qualifier == 'RELA':
                            result = ref
                        lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(
                            5, num_line, self._language))
                else:
                    raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                   field_name=field_name, value=", ".join(QUALIFIERS)))
            else:
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':20C:'))
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return result

    def _read_account_owner(self, lines):
        """ Read the number of the Owner's Account (Optional Field)"""
        result = {}
        field_name = "Party: Account Number"
        (num_line, field) = lines[0]
        if ":95P:" in field:  # option P
            mtch = re.match(r'^(%s):ACOW//(?P<code>%s)$' %
                            (R_TAG_P, R_FSET_BIC), field)
            if mtch:
                # store account number
                result['account_owner'] = {"code": mtch.group('code')}
                # all ok, pass line
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                            field_name=field_name, option="P", pattern=":ACOW//4!a2!a2!c[3!c]"))
        elif ":95R:" in field:  # option R
            mtch = re.match(r'^(%s):ACOW/(?P<dss>%s)/(?P<code>%s)$' % (R_TAG_P, alphanum(8),
                                                                        fsetx(34)), field)
            if mtch:
                # store account number
                result['account_owner'] = {"code": mtch.group('code'), "dss": mtch.group('dss')}
                # all ok, pass line
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                               field_name=field_name, option="R", pattern=":ACOW/8c/34x"))
        else:
            pass  # optional field, let it go

        return result

    def _read_safe_account(self, lines):
        """ Read the number of the Safekeeping Acoount (Mandatory Field) """
        field_name = "Account: Safekeeping Account"
        (num_line, field) = lines[0]
        if ":97A:" in field[0:5]:  # option P
            mtch = re.match('^(%s):SAFE\/\/(?P<code>%s)$' %
                            (R_TAG_P, fsetx(35)), field)
            if not mtch is None:
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                               field_name=field_name, option="A", pattern=":SAFE//35x"))
        elif ":97B:" in field[0:5]:  # option R
            mtch = re.match('^(%s):SAFE\/(?P<dss>%s)?\/(?P<type>%s)\/(?P<code>%s)$' % (R_TAG_P, alphanum(8),
                                                                                       alphanum_fixed(4), fsetx(35)), field)
            if not mtch is None:
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                               field_name=field_name, option="B", pattern=":SAFE/[8c]/4!c/35x"))
        else:
            raise ParsingError(_build_err_msg(
                1, num_line, self._language, tag=':97a:'))

    def _read_flags_block_a(self, lines):
        """ Read Block A Flags (Mandatory Field) """
        field_name = "Flag"
        result = {}
        # get ACTI flag first
        (num_line, field) = lines[0]
        mtch = re.match(r'^(?P<tag>%s):ACTI//(?P<flag>%s)$' %
                        (R_TAG_P, alpha_fixed(1)), field)

        if not mtch is None:
            if mtch.group('tag') != ':17B:':  # check tag code
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':17B:'))
            elif mtch.group('flag') not in ['Y', 'N']:
                raise ParsingError(_build_err_msg(6, num_line, self._language,
                                               subfield_name="flag", value="Y or N"))
            result.update({"acti": mtch.group('flag')}) # store acti flag
            lines.pop(0)
            # now get CONS flag
            (num_line, field) = lines[0]
            mtch = re.match(r'^(?P<tag>%s):CONS//(?P<flag>%s)$' %
                            (R_TAG_P, alpha_fixed(1)), field)
            if not mtch is None:
                if mtch.group('tag') != ':17B:':  # check tag code
                    raise ParsingError(
                        _build_err_msg(1, num_line, self._language, tag=':17B:'))
                elif mtch.group('flag') not in ['Y', 'N']:
                    raise ParsingError(_build_err_msg(
                        6, num_line, self._language, subfield_name="flag", value="Y, N"))
                else:
                    lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(
                    10, num_line, self._language, field_name=field_name, qualifier_value="CONS"))
        else:
            raise ParsingError(_build_err_msg(
                10, num_line, self._language, field_name=field_name, qualifier_value="ACTI"))
        return result

    def _read_start_of_block(self, lines, code):
        """ Start of block B """
        (num_line, field) = lines[0]
        mtch = re.match('^(%s)(%s)$' % (R_TAG_P, alphanum(16)), field)
        if mtch is not None:
            if mtch.group(1) != ':16R:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':16R:' + code))
            elif mtch.group(2) != code:
                raise ParsingError(_build_err_msg(
                    2, num_line, self._language, value=code))

            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_safe_account_block_b(self, lines):
        """ Read the number of the Safekeeping Acoount (Conditional Field) """
        field_name = "Account: Safekeeping Account"
        (num_line, field) = lines[0]
        if ":97A:" in field[0:5]:  # option P
            mtch = re.match('^(%s):SAFE\/\/(?P<code>%s)$' %
                            (R_TAG_P, fsetx(35)), field)
            if not mtch is None:
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                               field_name=field_name, option="A", pattern=":SAFE//35x"))
        elif ":97B:" in field[0:5]:  # option R
            mtch = re.match('^(%s):SAFE\/(?P<dss>%s)?\/(?P<type>%s)\/(?P<code>%s)$' % (R_TAG_P, alphanum(8),
                                                                                       alphanum_fixed(4), fsetx(35)), field)
            if not mtch is None:
                if mtch.group('dss') is None:
                    TYPE_CODES = ['ABDR', 'CEND',
                                  'DVPA', 'MARG', 'PHYS', 'SHOR']
                    if mtch.group('type') not in TYPE_CODES:
                        raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                       qualifier_value='SAFE', subfield_name="Account Type Code",
                                                       subfield_value=",".join(TYPE_CODES)))
                # All good
                lines.pop(0)
            else:
                raise ParsingError(_build_err_msg(7, num_line, self._language,
                                               field_name=field_name, option="B", pattern=":SAFE/[8c]/4!c/35x"))
        else:
            # HEY! CHECK FOR NETWORK RULE C7
            pass

    def _read_place_of_safekeeping(self, lines):
        """ Read the place of the Safekeeping entity (Optional Field) """
        field_name = "Place of Safekeeping"
        (num_line, field) = lines[0]
        mtch = re.match('^(?P<tag>%s):(?P<rest>.*)$' % (R_TAG_P), field)
        if not mtch is None:
            # define formats for each option
            opt_b = '(?P<qualifier>%s)\/(?P<dss>%s)?\/(?P<place>%s)(\/(?P<nar>%s))?' % (
                alphanum_fixed(4), alphanum(8), alphanum_fixed(4), fsetx(30))
            OPT_C = '(?P<qualifier>%s)\/\/(?P<country>%s)' % (alphanum_fixed(4),
                                                              alpha_fixed(2))
            OPT_F = '(?P<qualifier>%s)\/\/(?P<place>%s)\/(?P<bic>%s)' % (
                alphanum_fixed(4), alphanum_fixed(4), R_FSET_BIC)
            tag, field = mtch.group('tag'), mtch.group('rest')
            if '94B' in tag:
                mtch = re.match(opt_b, field)
                if not mtch is None:
                    qualifier, dss, place = mtch.group(
                        'qualifier'), mtch.group('dss'), mtch.group('place')
                    if qualifier == 'SAFE':
                        if dss is None and place != 'SHHE':
                            raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                           qualifier_value=qualifier, subfield_name="Place Code",
                                                           subfield_value='SHHE'))
                        else:  # all good
                            lines.pop(0)
                    else:
                        raise ParsingError(_build_err_msg(4, num_line, self._language, field_name=field_name,
                                                       value="'SAFE'"))

                else:
                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                   field_name=field_name, option="B", pattern=":SAFE/[8c]/4!c[/30x]"))

            elif '94C' in tag:
                mtch = re.match(OPT_C, field)
                if not mtch is None:
                    qualifier = mtch.group('qualifier')
                    if qualifier == 'SAFE':
                        lines.pop(0)  # all good
                    else:
                        raise ParsingError(_build_err_msg(4, num_line, self._language, field_name=field_name,
                                                       value="'SAFE'"))

                else:
                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                   field_name=field_name, option="C", pattern="SAFE//2!a"))

            elif '94F' in tag:
                mtch = re.match(OPT_F, field)
                if not mtch is None:
                    qualifier, place = mtch.group(
                        'qualifier'), mtch.group('place')
                    if qualifier == 'SAFE':
                        PLACE_VALUES = ['CUST', 'ICSD', 'NCSD', 'SHHE']
                        if place in PLACE_VALUES:
                            lines.pop(0)  # all good
                        else:
                            raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                           qualifier_value=qualifier, subfield_name="Place Code",
                                                           subfield_value=",".join(PLACE_VALUES)))

                    else:
                        raise ParsingError(_build_err_msg(4, num_line, self._language, field_name=field_name,
                                                       value="'SAFE'"))

                else:
                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                   field_name=field_name, option="F", pattern="SAFE//4!c/4!a2!a2!c[3!c]"))

            else:
                pass    # optional field

        pass

    def _read_activity_flag(self, lines):
        """ Read Block B Activity Flags (Conditional Field) """
        field_name = "Acticity Flag"
        # get ACTI flag first
        (num_line, field) = lines[0]
        mtch = re.match('^(?P<tag>%s):ACTI\/\/(?P<flag>%s)$' %
                        (R_TAG_P, alpha_fixed(1)), field)
        if not mtch is None:
            if mtch.group('tag') != ':17B:':  # check tag code
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':17B:'))
            elif mtch.group('flag') not in ['Y', 'N']:
                raise ParsingError(_build_err_msg(6, num_line, self._language,
                                               subfield_name="flag", value="Y or N"))
            lines.pop(0)
            # now get CONS flag
        else:
            pass  # Optional field

    def _read_end_of_block(self, lines, code):
        """ End of block B """
        (num_line, field) = lines[0]
        mtch = re.match('^(%s)(%s)$' % (R_TAG_P, alphanum(16)), field)
        if mtch is not None:
            if mtch.group(1) != ':16S:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':16S:' + code))
            elif mtch.group(2) != code:
                raise ParsingError(_build_err_msg(
                    2, num_line, self._language, value=code))

            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_isin(self, lines):
        """ Read Block B Activity Flags (Conditional Field) """
        result = {"isin" : {}}
        field_name = "Identification of the Financial Instrument"
        opt_b = '^(?P<tag>%s)(?P<rest>.+)$' % (R_TAG_P)
        (num_line, field) = lines[0]
        mtch = re.match(opt_b, field)
        if mtch is not None:
            tag, rest = mtch.group('tag'), mtch.group('rest')
            is_isin_present, is_description_present = False, False
            if tag == ':35B:':
                mtch = re.match('^ISIN(?P<idisin>.+)$', rest)
                if mtch:  # check ISIN Code (if exists)
                    is_isin_present = True
                    idisin = mtch.group('idisin')
                    mtch1 = re.match('^\s%s$' % alphanum_fixed(12), idisin)
                    if mtch1:
                        result['isin'].update({"code": idisin[1:]})
                        lines.pop(0)
                        (num_line, rest) = lines[0]
                    else:
                        raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                       field_name=field_name, subfield_name="ISIN", pattern="[ISIN 12!c][4*35x]"))

                # Check for description (if exists)
                if not is_swift_field_format_valid(rest) and is_setx_free(rest, 35):
                    is_description_present = True
                    result['isin'].update({"description": rest})
                    lines.pop(0)
                    (num_line, field) = lines[0]
                    if not is_swift_field_format_valid(field) and is_setx_free(field, 35):
                        result['isin']["description"] += " " + field
                        lines.pop(0)
                        (num_line, field) = lines[0]
                        if not is_swift_field_format_valid(field) and is_setx_free(field, 35):
                            result['isin']["description"] += " " + field
                            lines.pop(0)
                            (num_line, field) = lines[0]
                            if not is_swift_field_format_valid(field) and is_setx_free(field, 35):
                                result['isin']["description"] += " " + field
                                lines.pop(0)

                if not is_isin_present and not is_description_present:
                    raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                   field_name=field_name, option="B", pattern="[ISIN1!e12!c][4*35x]"))

            else:  # wrong tag code
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':35B:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _read_price(self, lines):
        """ Read the price of the financial instrument (Optional Field)"""
        result = {}
        (num_line, field) = lines[0]
        field_name = "Price"
        tag_number = '90'
        options = ['A', 'B']
        qualifiers = ['INDC', 'MRKT']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s):?(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[3], mtch.group('rest')
            if tag_num == tag_number:
                if opt == 'A':
                    regex = r"^(?P<qualifier>%s)//(?P<type>%s)/(?P<price>%s)$" % (
                        alphanum_fixed(4), alphanum_fixed(4), decimal(15))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier, typ, price = mtch1.group('qualifier'), mtch1.group('type'), mtch1.group('price')
                        if qualifier in qualifiers:
                            # store price
                            if qualifier == "MRKT":
                                result['market_price'] = {"percentage_type": typ, "price": float(price.replace(',','.'))}
                            else:
                                result['estimated_price'] = {"percentage_type": typ, "price": float(price.replace(',','.'))}
                            lines.pop(0) # all ok
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                       field_name=field_name, value=",".join(qualifiers)))
                    else:
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="A", pattern=":4!c//4!c/15d"))
                    
                elif opt == 'B':
                    regex = r"^(?P<qualifier>%s)//(?P<type>%s)/(?P<code>%s)(?P<price>%s)$" % (alphanum_fixed(4), alphanum_fixed(4), alpha_fixed(3), decimal(15))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier, typ, code, price = mtch1.group('qualifier'), mtch1.group('type'), mtch1.group("code"), mtch1.group('price')
                        if qualifier in qualifiers:
                            # store price
                            if qualifier == "MRKT":
                                result['market_price'] = {"amount_type": typ, "currency_code": code, "price": float(price.replace(',','.'))}
                            else:
                                result['estimated_price'] = {"amount_type": typ, "currency_code": code, "price": float(price.replace(',','.'))}
                            lines.pop(0) # all ok
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                       field_name=field_name, value=",".join(qualifiers)))
                    else:
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="B", pattern=":4!c//4!c/3!a15d"))
                else:
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                pass  # optional Field

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return result

    def _read_price_source(self, lines):
        """ Read the source of the price of the Financial instrument (Optional Field)"""
        (num_line, field) = lines[0]
        tag_number = '94'
        options = ['B']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s)(:)?(.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt = mtch.group('tag')[1:3], mtch.group('tag')[3]
            if tag_num == tag_number:
                if opt in options:
                    lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                pass  # optional Field

        else:  # not a valid swift's field format

            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_price_quotation_date(self, lines):
        (num_line, field) = lines[0]
        tag_number = '98'
        options = ['A', 'B']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s)(:)?(.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt = mtch.group('tag')[1:3], mtch.group('tag')[3]
            if tag_num == tag_number:
                if opt in options:
                    lines.pop(0)
                else:
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                pass  # optional Field

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_balance(self, lines):
        """ Read Balance (Optional Field)"""
        result = {}
        (num_line, field) = lines[0]
        field_name = "Balance"
        tag_number = '93'
        options = ['B']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s)(?P<rest>:?.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:
                if opt in options:
                    regex = "^:(?P<qualifier>%s)/(?P<dss>%s)?/(?P<type>%s)/(?P<sign>N)?(?P<balance>%s)$" % (alphanum_fixed(4),
                                                                                               alphanum(8), alphanum_fixed(4), decimal(15))
                    mtch1 = re.match(regex, rest)
                    if mtch1:  # check field format
                        qualifier, dss, sign, typ, balance = mtch1.group(
                            'qualifier'), mtch1.group('dss'), mtch1.group('sign'), mtch1.group('type'), mtch1.group('balance')
                        if qualifier in ['FIOP', 'INOP', 'FICL', 'INCL']:  # check qualifier
                            # check quantity type code
                            if not dss and not typ in ['AMOR', 'FAMT', 'UNIT']:
                                raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                               qualifier_value=qualifier, subfield_name="Quantity Type Code",
                                                               subfield_value=",".join(['AMOR', 'FAMT', 'UNIT'])))
                            else:  # all ok
                                sign = -1 if sign else 1
                                balance =  float(balance.replace(',','.'))*sign
                                if qualifier in ["FIOP", "INOP"]:
                                    result['opening_balance'] = {"balance": balance, "type": typ}
                                    if dss: result['opening_balance'].update({"dss": dss})
                                elif qualifier in ["FICL", "INCL"]:
                                    result['closing_balance'] = {"balance": balance, "type": typ}
                                    if dss: result['opening_balance'].update({"dss": dss})
                                lines.pop(0)
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(['FIOP', 'INOP', 'FICL', 'INCL'])))
                    else:
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="B", pattern=":4!c/[8c]/4!c/[N]15d"))

                else:
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                pass  # optional Field

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result 

    def _read_quantity_fi(self, lines):
        """ Read Quantity of Financial Instrument (Mandatory Field) """
        result = {}
        (num_line, field) = lines[0]
        field_name = "Quantity of Financial Instrument: Posting Quantity"
        tag_number = '36'
        options = ['B']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        # catch tag and the rest of field
        mtch = re.match('^(?P<tag>%s):(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:  # check field tag
                if opt in options:  # check field option
                    regex = r"^(?P<qualifier>%s)//(?P<type>%s)/(?P<quantity>%s)$" % (
                        alphanum_fixed(4), alphanum_fixed(4), decimal(15))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier, dss, typ, quantity = mtch1.group(
                            'qualifier'), mtch1.group('type'), mtch1.group('type'), mtch1.group('quantity')
                        if qualifier == 'PSTA':  # check qualifier
                            if dss in ['AMOR', 'FAMT', 'UNIT']:
                                result = {"type": typ, "quantity": float(quantity.replace(',', '.'))}
                                lines.pop(0)  # all ok
                            else:
                                raise ParsingError(_build_err_msg(9, num_line, self._language, field_name=field_name,
                                                               qualifier_value=qualifier, subfield_name="Quantity Type Code",
                                                               subfield_value=",".join(['AMOR', 'FAMT', 'UNIT'])))

                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value="PSTA"))
                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="B", pattern=":4!c//4!c/15d"))

                else:  # not a valid option for this field
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))

            else:  # wrong tag code, mandatory
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':36B:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return result

    def _read_indicator2(self, lines):
        """ Read Transaction Details Indicator  (Mandatory Field)"""
        (num_line, field) = lines[0]
        field_name = "Indicator"
        tag_number = '22'
        options = ['F', 'H']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s):(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:

                if opt == 'F':
                    regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<indicator>%s)$" % (alphanum_fixed(4),
                                                                                    alphanum(8), alphanum_fixed(4))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        dss, indicator = mtch1.group('dss'), mtch1.group('indicator')
                        result = {"indicator": indicator}
                        if dss:
                            result.update({"dss": dss})
                        lines.pop(0)  # all ok

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="F", pattern=":4!c/[8c]/4!c"))

                elif opt == 'H':

                    regex = "^(?P<qualifier>%s)//(?P<indicator>%s)$" % (alphanum_fixed(4),
                                                                        alphanum_fixed(4))
                    mtch1 = re.match(regex, rest)
                    if mtch1:  # check field format
                        indicator = mtch1.group('indicator')
                        result = indicator
                        lines.pop(0)  # all ok

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="H", pattern=":4!c//4!c"))

                else:  # not a valid option for this field
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                # wrong tag code, mandatory
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':22a:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return result

    def _read_transaction_details_date(self, lines):
        """ Read Transaction Details Indicator  (Mandatory Field)"""
        result = ""
        (num_line, field) = lines[0]
        field_name = "Transaction Detail Date"
        tag_number = '98'
        options = ['A', 'B', 'C']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s):(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:
                if opt == 'A':
                    regex = "^(?P<qualifier>%s)//%s$" % (alphanum_fixed(4), R_FDATE)
                    mtch1 = re.match(regex, rest)

                    if mtch1:
                        if not is_correct_date(mtch1.group('date')):
                            raise ParsingErroror(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="date",
                                                           pattern="YYYYMMDD"))
                        else:
                            result = mtch1.group('date')
                            lines.pop(0)  # all ok

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="A", pattern=":4!c//8!n"))

                elif opt == 'B':
                    regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<code>%s)$" % (
                        alphanum_fixed(4), alphanum(8), alphanum_fixed(4))
                    mtch1 = re.match(regex, rest)
                    if mtch1:  # check field format

                        lines.pop(0)  # all ok

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="H", pattern=":4!c/[8c]/4!c"))

                elif opt == 'C':
                    regex = "^(?P<qualifier>%s)//%s%s$" % (alphanum_fixed(4),
                                                           R_FDATE, R_FTIME)
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        if not is_correct_date(mtch1.group('date')):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="date",
                                                           pattern="YYYYMMDD"))
                        elif not is_correct_time(mtch1.group('time')):
                            raise ParsingError(_build_err_msg(8, num_line, self._language,
                                                           field_name=field_name, subfield_name="time", pattern="HHMMSS"))

                        result = mtch1.group('date')+mtch1.group('time')
                        lines.pop(0)  # all ok

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="C", pattern=":4!c//8!n6!n"))

                else:  # not a valid option for this field
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                # wrong tag code, mandatory
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':98a:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _read_transaction_details_party(self, lines):
        """ Read Transaction Details Party  (Mandatory Field)"""
        (num_line, field) = lines[0]
        field_name = "Party"
        tag_number = '95'
        options = ['C', 'P', 'Q', 'R']
        qualifiers = ['BUYR', 'DEAG', 'DECU', 'DEI1', 'DEI2',
                      'PSET', 'REAG', 'RECU', 'REI1', 'REI2', 'SELL']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        mtch = re.match('^(?P<tag>%s):(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:
                if opt == 'C':
                    regex = "^(?P<qualifier>%s)//%s$" % (alphanum_fixed(4),
                                                         alpha_fixed(2))
                    mtch1 = re.match(regex, rest)
                    if mtch1:

                        qualifier = mtch1.group('qualifier')
                        if qualifier in qualifiers:
                            lines.pop(0)  # all ok
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(qualifiers)))

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="C", pattern=":4!c//2!a"))
                elif opt == 'P':
                    regex = "^(?P<qualifier>%s)//%s$" % (alphanum_fixed(4), R_FSET_BIC)
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier = mtch1.group('qualifier')
                        if qualifier in qualifiers:
                            lines.pop(0)  # all ok
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(qualifiers)))

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="P", pattern=":4!c//4!a2!a2!c[3!c]"))

                elif opt == 'R':
                    regex = "^(?P<qualifier>%s)/(?P<dss>%s)?/(?P<code>%s)$" % (
                        alphanum_fixed(4), alphanum(8), fsetx(34))
                    mtch1 = re.match(regex, rest)
                    if mtch1:  # check field format
                        qualifier = mtch1.group('qualifier')
                        if qualifier in qualifiers:
                            lines.pop(0)  # all ok
                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(qualifiers)))
                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="R", pattern=":4!c/[8c]/4!c"))

                elif opt == 'Q':
                    regex = "^(?P<qualifier>%s)//(?P<address>%s)$" % (
                        alphanum_fixed(4), fsetx(35))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier, address = mtch1.group(
                            'qualifier'), mtch1.group('address'),
                        if qualifier not in qualifiers:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(qualifiers)))
                        # parse address
                        if not is_swift_field_format_valid(address):
                            lines.pop(0)
                            (num_line, field) = lines[0]
                            if not is_swift_field_format_valid(field) and is_setx(field, 35):

                                lines.pop(0)
                                (num_line, field) = lines[0]
                                if not is_swift_field_format_valid(field) and is_setx(field, 35):
                                    lines.pop(0)
                                    (num_line, field) = lines[0]
                                    if not is_swift_field_format_valid(field) and is_setx(field, 35):
                                        lines.pop(0)
                        else:
                            raise ParsingError(_build_err_msg(7, num_line, self._language,
                                                           field_name=field_name, option="Q", pattern=":4!c//4*35x"))

                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="Q", pattern=":4!c//4*35x6!n"))

                else:  # not a valid option for this field
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))
            else:
                # wrong tag code, mandatory
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':98a:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_party_reference(self, lines):
        """ Read Message's sender Reference """
        field_name = "Processing Reference"
        (num_line, field) = lines[0]
        mtch = re.match(r'^(%s):(%s)//(.*)$' %
                        (R_TAG_P, R_FSET_ALPHANUM), field)
        if mtch is not None:
            if mtch.group(1) != ':20C:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':20C:'))
            elif mtch.group(2) != 'PROC':
                raise ParsingError(_build_err_msg(
                    4, num_line, self._language, field_name=field_name, value='\'PROC\''))
            elif re.match(fsetx(16), mtch.group(3)) is None:
                raise ParsingError(_build_err_msg(5, num_line, self._language))
            lines.pop(0)
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))

    def _read_narrative(self, lines):
        """ Read Message's sender Reference """
        result = ""
        field_name = "Processing Reference"
        (num_line, field) = lines[0]
        mtch = re.match(r'^(%s):(%s)//(?P<narrative>.+)$' %
                        (R_TAG_P, R_FSET_ALPHANUM), field)
        if mtch is not None:
            if mtch.group(1) != ':70E:':
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':70E:'))
            elif mtch.group(2) != 'TRDE':
                raise ParsingError(_build_err_msg(
                    4, num_line, self._language, field_name=field_name, value='\'PROC\''))
            elif re.match(fsetx(16), mtch.group(3)) is None:
                raise ParsingError(_build_err_msg(5, num_line, self._language))
            result = mtch.group('narrative') # store narrative
            lines.pop(0) # all ok
            for _ in range(9): # up to 10 lines of commentaries
                (num_line, field) = lines[0]
                if is_swift_field_format_valid(field) or not is_setx(field, 35):
                    break
                result += " " + field
                lines.pop(0)
                    
        else:
            raise ParsingError(_build_err_msg(0, num_line, self._language))
        return {"narrative": result}

    def _read_amount(self, lines):
        """ Amount (Mandatory Field) """
        result = {}
        (num_line, field) = lines[0]
        field_name = "Amount"
        tag_number = '19'
        options = ['A']
        qualifiers = ['PSTA', 'ACRU']
        valid_tags = list(map(lambda x: ':%s%s:' % (tag_number, x), options))
        # catch tag and the rest of field
        mtch = re.match('^(?P<tag>%s):(?P<rest>.+)$' % (R_TAG_P), field)
        if mtch:
            tag_num, opt, rest = mtch.group('tag')[1:3], mtch.group('tag')[
                3], mtch.group('rest')
            if tag_num == tag_number:  # check field tag
                if opt in options:  # check field option
                    regex = r"^(?P<qualifier>%s)//(?P<sign>N)?(?P<code>%s)(?P<amount>%s)$" % (
                        alphanum_fixed(4), alpha_fixed(3), decimal(15))
                    mtch1 = re.match(regex, rest)
                    if mtch1:
                        qualifier, sign, code, amount = mtch1.group(
                            'qualifier'), mtch1.group('sign'), mtch1.group('code'), mtch1.group('amount')
                        if qualifier in qualifiers:  # check qualifier
                            if qualifier == 'PSTA':
                                amount = float(amount.replace(',','.'))*(-1 if sign else 1)
                                result = {"amount" : amount, "currency_code": code}
                            lines.pop(0)  # all ok

                        else:
                            raise ParsingError(_build_err_msg(4, num_line, self._language,
                                                           field_name=field_name, value=",".join(qualifiers)))
                    else:  # subfields format not correct
                        raise ParsingError(_build_err_msg(
                            7, num_line, self._language, field_name=field_name, option="A", pattern=":4!c//[N]3!a15d"))

                else:  # not a valid option for this field
                    raise ParsingError(_build_err_msg(
                        11, num_line, self._language, tag=', '.join(valid_tags)))

            else:  # wrong tag code
                raise ParsingError(_build_err_msg(
                    1, num_line, self._language, tag=':19A:'))

        else:  # not a valid swift's field format
            raise ParsingError(_build_err_msg(0, num_line, self._language))

        return result

    def _parse_block_a(self, lines):
        """ Swift's MT536 message BlockA parsing """
        result = {}
        self._read_start_of_block(lines, 'GENL')
        result.update(self._read_page_number_indicator(lines))
        self._read_statement_number(lines)
        result.update(self._read_seme(lines))
        self._read_message_function(lines)
        self._read_preparation_date_time(lines)
        result.update(self._read_statement_period(lines))
        result.update(self._read_indicator1(lines))
        self._read_blocks_a1(lines)
        result.update(self._read_account_owner(lines))
        self._read_safe_account(lines)
        result.update(self._read_flags_block_a(lines))
        self._read_end_of_block(lines, 'GENL')
        return {"general": result}

    def _read_blocks_a1(self, lines):
        (num_line, field) = lines[0]
        while field == ':16R:LINK':
            lines.pop(0)
            self._read_linked_message(lines)
            self._read_reference_a1(lines)
            (num_line, field) = lines[0]
            if field != ':16S:LINK':  # Check for end of block A1
                raise ParsingError(_build_err_msg(0, num_line, self._language))
            else:
                lines.pop(0)
                (num_line, field) = lines[0]

    def _parse_blocks_b(self, lines):
        """ Swift's MT536 message BlocksB parsing """
        result = []
        while not _IS_EOF(lines) and not re.match(r':16R:SUBSAFE', lines[0][1]) is None:
            # parse block b and append info to list
            result.append(self._parse_block_b(lines))
        return {"accounts": result}

    def _parse_block_b(self, lines):
        """ Swift's MT536 message BlocksB parsing """
        result = {}
        self._read_start_of_block(lines, 'SUBSAFE')
        self._read_account_owner(lines)
        self._read_safe_account_block_b(lines)
        self._read_place_of_safekeeping(lines)
        self._read_activity_flag(lines)
        result.update(self._parse_blocks_b1(lines))
        self._read_end_of_block(lines, 'SUBSAFE')
        return result


    # BLOCKS B1
    def _parse_blocks_b1(self, lines):
        result = []
        while not re.match(r':16R:FIN', lines[0][1]) is None:
            result.append(self._parse_block_b1(lines))
        return {"financial_instruments": result}

    def _parse_block_b1(self, lines):
        result = {}
        self._read_start_of_block(lines, 'FIN')

        result.update(self._read_isin(lines))

        result.update(self._read_price(lines))

        self._read_price_source(lines)
        self._read_price_quotation_date(lines)

        result.update(self._read_balance(lines))
        result.update(self._read_balance(lines))
        result.update(self._parse_blocks_b1a(lines))
        self._read_end_of_block(lines, 'FIN')
        return result

    def _parse_blocks_b1a(self, lines):  # Mandatory Repetitive sequence
        result_out = []
        while True:
            result_in = {}
            self._read_start_of_block(lines, 'TRAN')
            result_in.update(self._parse_blocks_b1a1(lines))
            result_in.update(self._parse_block_b1a2(lines))
            self._read_end_of_block(lines, 'TRAN')
            result_out.append(result_in)
            if re.match(r':16R:TRAN', lines[0][1]) is None:
                break
        return {"transactions": result_out}

    def _parse_blocks_b1a1(self, lines):
        result = ""
        while True:
            self._read_start_of_block(lines, 'LINK')
            self._read_linked_message(lines)
            ref = self._read_reference_b1a1(lines)
            if ref != "":
                result = ref 
            self._read_end_of_block(lines, 'LINK')
            if re.match(r':16R:LINK', lines[0][1]) is None:
                break
        return {"rela": result}

    def _parse_block_b1a2(self, lines):
        """ Parsing Transaction Details Block """
        result = {}
        self._read_start_of_block(lines, 'TRANSDET')

        # ignore Place Optional Repetitive Field
        while re.search(r':94[BCFH]:', lines[0][1]):
            lines.pop(0)

        # Quantity Mandatory repetitive fields

        while True:
            result_in = []    
            result_in.append(self._read_quantity_fi(lines))
            if re.search(r':36B:', lines[0][1]) is None:
                break
        result.update({"quantity_fi": result_in})

        # Ignore Number of Days Accrued Field (Optional)
        if re.search(r':99A::DAAC/', lines[0][1]):
            lines.pop(0)

        # Amount Field(Optional Repetitive)
        if re.search(r':19A::PSTA/', lines[0][1]):
            result.update({"posting_amount": self._read_amount(lines)})
        if re.search(r':19A::ACRU/', lines[0][1]):
            self._read_amount(lines)

        # Indicator repetitive fields (Mandatories)
        if not re.search(r':22F::TRAN/', lines[0][1]):
            raise ParsingError(_build_err_msg(
                10, lines[0][0], self._language, field_name='Indicator', qualifier_value='TRAN'))
        self._read_indicator2(lines)
        if not re.search(r':22H::REDE/', lines[0][1]):
            raise ParsingError(_build_err_msg(10, lines[0][0], self._language, field_name="Indicator",
                                           qualifier_value='REDE'))
        # store receive/deliver mode
        result.update({"rede": self._read_indicator2(lines)})

        if not re.search(r':22H::PAYM/', lines[0][1]):
            raise ParsingError(_build_err_msg(10, lines[0][0], self._language, field_name="Indicator",
                                           qualifier_value='PAYM'))
        self._read_indicator2(lines)
        while re.search(r':22[A-Z]:', lines[0][1]):  # mandatory repetitive field
            self._read_indicator2(lines)

        # Date time fields (Mandatory Repetitive)
        if not re.search(r':98[A-C]::ESET/', lines[0][1]):
            raise ParsingError(_build_err_msg(10, lines[0][0], self._language, field_name='DATE/TIME',
                                           qualifier_value='ESET'))
        result.update({"eset": self._read_transaction_details_date(lines)})

        while re.search(r':98[A-Z]:', lines[0][1]):  # optional repetitive field
            self._read_transaction_details_date(lines)

         # Movement Status Field (Optional)
        if re.match(r':25D:', lines[0][1]):
            lines.pop(0) # just ignore field

        # Narrative field (Optional)
        if re.match(r':70E:', lines[0][1]):
            result.update(self._read_narrative(lines))
        
        self._read_blocks_b1a2a(lines)

        self._read_end_of_block(lines, 'TRANSDET')
        return {"details": result}

    def _read_blocks_b1a2a(self, lines):
        (_, field) = lines[0]
        while field == ':16R:SETPRTY':
            self._read_start_of_block(lines, 'SETPRTY')
            self._read_transaction_details_party(lines)
            (_, field) = lines[0]
            if re.search(':97[A-Z]:', field):  # check if safe account is included
                self._read_safe_account(lines)
            (_, field) = lines[0]
            if re.search(r':20[A-Z]:', field):  # check if reference is included
                self._read_party_reference(lines)
            self._read_end_of_block(lines, 'SETPRTY')
            (_, field) = lines[0]

    def _read_blocks_c(self, lines):
        """ Parse Additional Information """
        while not _IS_EOF(lines) and re.match(r':16R:ADDINFO', lines[0][1]):
            self._read_start_of_block(lines, 'ADDINFO')
            while not re.match(r':16[A-W]:', lines[0][1]):
                lines.pop(0)  # just ignore the block
            self._read_end_of_block(lines, 'ADDINFO')


### Execute ###
if __name__ == '__main__':
    PARSER = MT536Parser("in3.txt", 1)
    (no_errors, result) = PARSER.parse()
    print(pprint.pprint(result))
