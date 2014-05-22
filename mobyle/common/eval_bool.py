# -*- coding: utf-8 -*-


class EvalBoolFactory(object):

    def __init__(self, values={}):
        self.values = values

    def test(self, expr):
        if not(expr):
            return True
        result = True
        # 'variable'
        # means variable is truthy
        if isinstance(expr, basestring):
            return bool(self.values[expr])
        # {}
        # return true if all contained key/value tests are true
        elif isinstance(expr, dict):
            for key, value in expr.items():
                # iterate tests in the dict
                if key in self.values.keys():
                    # {'x':1} return true if values['x']==1
                    if isinstance(value, int) or isinstance(value, basestring)\
                        or isinstance(value, float) or isinstance(value, bool):
                            if self.values[key] != value:
                                result = False
                    elif isinstance(value, dict):
                        for operator, operand in value.items():
                            # comparison operators
                            if operator == '#gt':
                                result = self.values[key] > operand
                            elif operator == '#gte':
                                result = self.values[key] >= operand
                            elif operator == '#lt':
                                result = self.values[key] < operand
                            elif operator == '#lte':
                                result = self.values[key] <= operand
                            elif operator == '#in':
                                result = self.values[key] in operand
                            elif operator == '#ne':
                                result = self.values[key] != operand
                            elif operator == '#nin':
                                result = self.values[key] not in operand
                # logical operators
                elif key == '#or':
                    inner_result = True
                    for inner_test in value:
                        inner_result = self.test(inner_test)
                        if inner_result is True:
                            result = True
                            break
                    result = True
                elif key == '#and':
                    inner_result = True
                    for inner_test in value:
                        inner_result = self.test(inner_test)
                        if inner_result is False:
                            result = False
                            break
                elif key == '#not':
                    result = not(self.test(value))
                elif key == '#nor':
                    inner_result = True
                    for inner_test in value:
                        inner_result = not(self.test(inner_test))
                        if inner_result is False:
                            result = False
                            break
                # break on first unmet condition
                if result is False:
                    break
        # []
        # return false on first condition not met
        elif isinstance(expr, list):
            for test_item in expr:
                result = self.test(test_item)
                if result is False:
                    break
        return result

