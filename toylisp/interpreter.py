'''
Help, guidance and core functions from:
1. http://norvig.com/lispy.html
2. http://theory.stanford.edu/~amitp/yapps/yapps-doc/node2.html for grammar
3. http://www.dabeaz.com/ply/ply.html
'''


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        return str(token)

is_atom = lambda v: isinstance(v, str)
is_literal = lambda v: not isinstance(v, list)


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        return self.get(var, self.outer.find(var) if self.outer else None)


def add_globals(env):
    "Add some Lisp standard procedures to an environment."
    import operator as op
    from functools import reduce
    reducer = lambda o: lambda *args: reduce(o, args)
    env.update({
        '+': reducer(op.add),
        '-': reducer(op.sub),
        '*': reducer(op.mul),
        '/': reducer(op.truediv),
        'not': op.not_,
        '>':  op.gt,
        '<':  op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=':  op.eq,
        'eq?': op.eq,
        'cons': lambda x, y: [x]+y,
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'atom?': is_atom,
        'else': True
    })
    return env

global_env = add_globals(Env())


def notbound(var):
    raise NameError("symbol '%s' is not bound to a value" % var)


def eval(e, env=global_env):
    "Evaluate an expression in an environment."
    if is_atom(e):          # variable reference
        value = env.find(e)
        return value if value is not None else notbound(e)
    elif is_literal(e):     # constant literal
        return e
    elif e[0] == 'quote':   # (quote exp)
        (_, exp) = e
        return exp
    elif e[0] == 'cond':    # (if test conseq alt)
        (_, *forms) = e
        for test, result in forms:
            if eval(test, env):
                return eval(result, env)
    elif e[0] == 'define':  # (define var exp)
        (_, var, exp) = e
        env[var] = eval(exp, env)
    elif e[0] == 'lambda':  # (lambda (var*) exp)
        (_, vars, exp) = e
        return lambda *args: eval(exp, Env(vars, args, env))
    else:                  # (proc exp*)
        exps = [eval(exp, env) for exp in e]
        proc = exps.pop(0)
        return proc(*exps)


def lispify(value):
    return str(value) if is_literal(value) else "("+(" ".join(
        lispify(v) for v in value))+")"
