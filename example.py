from kunoichi import Task
from glob import iglob

t = Task('build_luajit')

@t.rule
def cc(cfg):
    return 'cl /nologo /c /Fo$out $in'

@t.rule(rspfile='$out.rsp', rspfile_content='$in')
def link(cfg):
    return 'link /nologo /out:$out @$out.rsp'

@t.rule
def mt(cfg):
    return 'cmd /c if exist $in (mt /nologo -manifest $in -outputresource:$out'

@t.rule(rspfile='$out.rsp', rspfile_content='$in')
def lib(cfg):
    return 'lib /nologo /out:$out @$out.rsp'


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


print t.generate(None)
