# Generated from AegisLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .AegisLangParser import AegisLangParser
else:
    from AegisLangParser import AegisLangParser

# This class defines a complete listener for a parse tree produced by AegisLangParser.
class AegisLangListener(ParseTreeListener):

    # Enter a parse tree produced by AegisLangParser#program.
    def enterProgram(self, ctx:AegisLangParser.ProgramContext):
        pass

    # Exit a parse tree produced by AegisLangParser#program.
    def exitProgram(self, ctx:AegisLangParser.ProgramContext):
        pass


    # Enter a parse tree produced by AegisLangParser#moduleDecl.
    def enterModuleDecl(self, ctx:AegisLangParser.ModuleDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#moduleDecl.
    def exitModuleDecl(self, ctx:AegisLangParser.ModuleDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#structDecl.
    def enterStructDecl(self, ctx:AegisLangParser.StructDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#structDecl.
    def exitStructDecl(self, ctx:AegisLangParser.StructDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#fieldDecl.
    def enterFieldDecl(self, ctx:AegisLangParser.FieldDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#fieldDecl.
    def exitFieldDecl(self, ctx:AegisLangParser.FieldDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#enumDecl.
    def enterEnumDecl(self, ctx:AegisLangParser.EnumDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#enumDecl.
    def exitEnumDecl(self, ctx:AegisLangParser.EnumDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#enumVariant.
    def enterEnumVariant(self, ctx:AegisLangParser.EnumVariantContext):
        pass

    # Exit a parse tree produced by AegisLangParser#enumVariant.
    def exitEnumVariant(self, ctx:AegisLangParser.EnumVariantContext):
        pass


    # Enter a parse tree produced by AegisLangParser#fnDecl.
    def enterFnDecl(self, ctx:AegisLangParser.FnDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#fnDecl.
    def exitFnDecl(self, ctx:AegisLangParser.FnDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#paramList.
    def enterParamList(self, ctx:AegisLangParser.ParamListContext):
        pass

    # Exit a parse tree produced by AegisLangParser#paramList.
    def exitParamList(self, ctx:AegisLangParser.ParamListContext):
        pass


    # Enter a parse tree produced by AegisLangParser#parameter.
    def enterParameter(self, ctx:AegisLangParser.ParameterContext):
        pass

    # Exit a parse tree produced by AegisLangParser#parameter.
    def exitParameter(self, ctx:AegisLangParser.ParameterContext):
        pass


    # Enter a parse tree produced by AegisLangParser#constDecl.
    def enterConstDecl(self, ctx:AegisLangParser.ConstDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#constDecl.
    def exitConstDecl(self, ctx:AegisLangParser.ConstDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#primitiveType.
    def enterPrimitiveType(self, ctx:AegisLangParser.PrimitiveTypeContext):
        pass

    # Exit a parse tree produced by AegisLangParser#primitiveType.
    def exitPrimitiveType(self, ctx:AegisLangParser.PrimitiveTypeContext):
        pass


    # Enter a parse tree produced by AegisLangParser#userDefinedType.
    def enterUserDefinedType(self, ctx:AegisLangParser.UserDefinedTypeContext):
        pass

    # Exit a parse tree produced by AegisLangParser#userDefinedType.
    def exitUserDefinedType(self, ctx:AegisLangParser.UserDefinedTypeContext):
        pass


    # Enter a parse tree produced by AegisLangParser#optionType.
    def enterOptionType(self, ctx:AegisLangParser.OptionTypeContext):
        pass

    # Exit a parse tree produced by AegisLangParser#optionType.
    def exitOptionType(self, ctx:AegisLangParser.OptionTypeContext):
        pass


    # Enter a parse tree produced by AegisLangParser#resultType.
    def enterResultType(self, ctx:AegisLangParser.ResultTypeContext):
        pass

    # Exit a parse tree produced by AegisLangParser#resultType.
    def exitResultType(self, ctx:AegisLangParser.ResultTypeContext):
        pass


    # Enter a parse tree produced by AegisLangParser#arrayType.
    def enterArrayType(self, ctx:AegisLangParser.ArrayTypeContext):
        pass

    # Exit a parse tree produced by AegisLangParser#arrayType.
    def exitArrayType(self, ctx:AegisLangParser.ArrayTypeContext):
        pass


    # Enter a parse tree produced by AegisLangParser#statement.
    def enterStatement(self, ctx:AegisLangParser.StatementContext):
        pass

    # Exit a parse tree produced by AegisLangParser#statement.
    def exitStatement(self, ctx:AegisLangParser.StatementContext):
        pass


    # Enter a parse tree produced by AegisLangParser#variableDecl.
    def enterVariableDecl(self, ctx:AegisLangParser.VariableDeclContext):
        pass

    # Exit a parse tree produced by AegisLangParser#variableDecl.
    def exitVariableDecl(self, ctx:AegisLangParser.VariableDeclContext):
        pass


    # Enter a parse tree produced by AegisLangParser#assignmentStmt.
    def enterAssignmentStmt(self, ctx:AegisLangParser.AssignmentStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#assignmentStmt.
    def exitAssignmentStmt(self, ctx:AegisLangParser.AssignmentStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#returnStmt.
    def enterReturnStmt(self, ctx:AegisLangParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#returnStmt.
    def exitReturnStmt(self, ctx:AegisLangParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#ifStmt.
    def enterIfStmt(self, ctx:AegisLangParser.IfStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#ifStmt.
    def exitIfStmt(self, ctx:AegisLangParser.IfStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#forStmt.
    def enterForStmt(self, ctx:AegisLangParser.ForStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#forStmt.
    def exitForStmt(self, ctx:AegisLangParser.ForStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#whileStmt.
    def enterWhileStmt(self, ctx:AegisLangParser.WhileStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#whileStmt.
    def exitWhileStmt(self, ctx:AegisLangParser.WhileStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#expressionStmt.
    def enterExpressionStmt(self, ctx:AegisLangParser.ExpressionStmtContext):
        pass

    # Exit a parse tree produced by AegisLangParser#expressionStmt.
    def exitExpressionStmt(self, ctx:AegisLangParser.ExpressionStmtContext):
        pass


    # Enter a parse tree produced by AegisLangParser#constructorOrFunctionExpr.
    def enterConstructorOrFunctionExpr(self, ctx:AegisLangParser.ConstructorOrFunctionExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#constructorOrFunctionExpr.
    def exitConstructorOrFunctionExpr(self, ctx:AegisLangParser.ConstructorOrFunctionExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#orExpr.
    def enterOrExpr(self, ctx:AegisLangParser.OrExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#orExpr.
    def exitOrExpr(self, ctx:AegisLangParser.OrExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#additiveExpr.
    def enterAdditiveExpr(self, ctx:AegisLangParser.AdditiveExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#additiveExpr.
    def exitAdditiveExpr(self, ctx:AegisLangParser.AdditiveExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#awaitExpr.
    def enterAwaitExpr(self, ctx:AegisLangParser.AwaitExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#awaitExpr.
    def exitAwaitExpr(self, ctx:AegisLangParser.AwaitExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#relationalExpr.
    def enterRelationalExpr(self, ctx:AegisLangParser.RelationalExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#relationalExpr.
    def exitRelationalExpr(self, ctx:AegisLangParser.RelationalExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#parenExpr.
    def enterParenExpr(self, ctx:AegisLangParser.ParenExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#parenExpr.
    def exitParenExpr(self, ctx:AegisLangParser.ParenExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#indexExpr.
    def enterIndexExpr(self, ctx:AegisLangParser.IndexExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#indexExpr.
    def exitIndexExpr(self, ctx:AegisLangParser.IndexExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#methodCallExpr.
    def enterMethodCallExpr(self, ctx:AegisLangParser.MethodCallExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#methodCallExpr.
    def exitMethodCallExpr(self, ctx:AegisLangParser.MethodCallExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#unaryExpr.
    def enterUnaryExpr(self, ctx:AegisLangParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#unaryExpr.
    def exitUnaryExpr(self, ctx:AegisLangParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#primaryExpr.
    def enterPrimaryExpr(self, ctx:AegisLangParser.PrimaryExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#primaryExpr.
    def exitPrimaryExpr(self, ctx:AegisLangParser.PrimaryExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#memberAccessExpr.
    def enterMemberAccessExpr(self, ctx:AegisLangParser.MemberAccessExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#memberAccessExpr.
    def exitMemberAccessExpr(self, ctx:AegisLangParser.MemberAccessExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#multiplicativeExpr.
    def enterMultiplicativeExpr(self, ctx:AegisLangParser.MultiplicativeExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#multiplicativeExpr.
    def exitMultiplicativeExpr(self, ctx:AegisLangParser.MultiplicativeExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#equalityExpr.
    def enterEqualityExpr(self, ctx:AegisLangParser.EqualityExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#equalityExpr.
    def exitEqualityExpr(self, ctx:AegisLangParser.EqualityExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#conditionalExpr.
    def enterConditionalExpr(self, ctx:AegisLangParser.ConditionalExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#conditionalExpr.
    def exitConditionalExpr(self, ctx:AegisLangParser.ConditionalExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#andExpr.
    def enterAndExpr(self, ctx:AegisLangParser.AndExprContext):
        pass

    # Exit a parse tree produced by AegisLangParser#andExpr.
    def exitAndExpr(self, ctx:AegisLangParser.AndExprContext):
        pass


    # Enter a parse tree produced by AegisLangParser#expressionList.
    def enterExpressionList(self, ctx:AegisLangParser.ExpressionListContext):
        pass

    # Exit a parse tree produced by AegisLangParser#expressionList.
    def exitExpressionList(self, ctx:AegisLangParser.ExpressionListContext):
        pass


    # Enter a parse tree produced by AegisLangParser#integerLiteral.
    def enterIntegerLiteral(self, ctx:AegisLangParser.IntegerLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#integerLiteral.
    def exitIntegerLiteral(self, ctx:AegisLangParser.IntegerLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#floatLiteral.
    def enterFloatLiteral(self, ctx:AegisLangParser.FloatLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#floatLiteral.
    def exitFloatLiteral(self, ctx:AegisLangParser.FloatLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#stringLiteral.
    def enterStringLiteral(self, ctx:AegisLangParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#stringLiteral.
    def exitStringLiteral(self, ctx:AegisLangParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:AegisLangParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:AegisLangParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#identifierLiteral.
    def enterIdentifierLiteral(self, ctx:AegisLangParser.IdentifierLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#identifierLiteral.
    def exitIdentifierLiteral(self, ctx:AegisLangParser.IdentifierLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#noneLiteral.
    def enterNoneLiteral(self, ctx:AegisLangParser.NoneLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#noneLiteral.
    def exitNoneLiteral(self, ctx:AegisLangParser.NoneLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#arrayLiteral.
    def enterArrayLiteral(self, ctx:AegisLangParser.ArrayLiteralContext):
        pass

    # Exit a parse tree produced by AegisLangParser#arrayLiteral.
    def exitArrayLiteral(self, ctx:AegisLangParser.ArrayLiteralContext):
        pass


    # Enter a parse tree produced by AegisLangParser#identifier.
    def enterIdentifier(self, ctx:AegisLangParser.IdentifierContext):
        pass

    # Exit a parse tree produced by AegisLangParser#identifier.
    def exitIdentifier(self, ctx:AegisLangParser.IdentifierContext):
        pass



del AegisLangParser