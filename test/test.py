#!/usr/bin/python
from pycunparser.c_generator import CGenerator
from pycunparser.c_ast import *

def int_const(n):
    return Constant('int', str(n))
def enum_item(key, value):
    return Enumerator(key,int_const(value), postcomment = '0x%08x' % value)

ast = FileAST([
    Decl(None, [], [], [], Enum(
        "test_enum",
        EnumeratorList(
            [enum_item('A', 10),
             enum_item('B', 20),
             enum_item('C', 30)
            ])
        ), None, None),
    DummyNode(postcomment="12345"),
    Decl(None, [], [], [], Struct(
        "test_struct",
            [Decl('A',[],[],[],TypeDecl('ax',[],IdentifierType(['int'])), None, 
               Constant('int', '20'), postcomment='123'),
            Decl('A',[],[],[],TypeDecl('bx',[],IdentifierType(['int'])), None, 
               Constant('int', '20'))]
        ), None, None),
    Typedef('aaf', [], ['typedef'], TypeDecl('declname',[],Struct('z',[]))),
    Typedef('aaf2', [], ['typedef'], TypeDecl('declname',[],Struct(None,[
            Decl('A',[],[],[],TypeDecl('ax',[],IdentifierType(['int'])), None, 
               Constant('int', '20'), postcomment='123'),
        ]))),
    Typedef('aaf2', [], ['typedef'], PtrDecl([], TypeDecl('declname',[],Struct(None,[
            Decl('A',[],[],[],TypeDecl('ax',[],IdentifierType(['int'])), None, 
               Constant('int', '20'), postcomment='123'),
        ])))),
    Typedef('funcptr', [], ['typedef'], PtrDecl(
        [], FuncDecl(ParamList([
                Decl('arg0',[],[],[],TypeDecl('arg0',[],IdentifierType(['int'])), None, None),
                Decl('arg1',[],[],[],TypeDecl('arg1',[],IdentifierType(['int'])), None, None)
            ]), TypeDecl('funcptr',[],IdentifierType(['int'])))
        )),
    FuncDecl(ParamList([
            Decl('arg0',[],[],[],TypeDecl('arg0',[],IdentifierType(['int'])), None, None),
            Decl('arg1',[],[],[],TypeDecl('arg1',[],IdentifierType(['int'])), None, None)
        ]), TypeDecl('func',[],IdentifierType(['int'])))
    ],
    )

gen = CGenerator()
print gen.visit(ast)

