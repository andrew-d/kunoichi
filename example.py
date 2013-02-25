from kunoichi import Task, config, do_config
from glob import iglob

@config
def set_flags(cfg):
    cfg.c.CFLAGS = '/nologo /MTd /O2 /W3 /D_CRT_SECURE_NO_DEPRECATE /c'
    cfg.c.LFLAGS = '/nologo'
    cfg.c.LIBFLAGS = '/nologo'


t = Task('build_luajit')

@t.rule
def cc(cfg):
    return 'cl {cfg.c.CFLAGS} /Fo$out $in'

@t.rule(rspfile='$out.rsp', rspfile_content='$in')
def link(cfg):
    return 'link {cfg.c.LFLAGS} /out:$out @$out.rsp'

@t.rule
def mt(cfg):
    return 'cmd /c if exist $in (mt /nologo -manifest $in -outputresource:$out)'

@t.rule(rspfile='$out.rsp', rspfile_content='$in')
def lib(cfg):
    return 'lib {cfg.c.LFLAGS} /out:$out @$out.rsp'


@t.build
def build_minilua(cfg):
    return [
        ('minilua.obj', 'cc', 'host/minilua.c'),
        {'outputs': 'minilua.exe', 'rule': 'link', 'inputs': 'minilua.obj'},
    ]

@t.build
def build_luajit(cfg):
    for f in iglob('*.py'):
        yield ('foobar', 'other', f)


cfg = do_config()
print t.generate(cfg)
