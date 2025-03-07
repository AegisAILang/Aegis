grammar AegisLang;

/**
 * Aegis - AI-Optimized Programming Language Grammar
 * This grammar file defines the syntax for the Aegis programming language,
 * which is specifically designed for deterministic and error-free AI code generation.
 * 
 * @ai:best-practices Follow these conventions for AI-optimized code generation:
 * - Use clear, descriptive names that convey purpose
 * - Prefer explicit type annotations over inference
 * - Create small, focused modules with clear responsibilities
 * - Document all public interfaces with /// comments
 */

// Parser Rules
/**
 * The entry point for an Aegis program.
 * A program consists of one or more module declarations.
 * 
 * @ai:preferred Organize code into logical modules with clear responsibilities.
 * Each module should focus on a single domain or feature set.
 */
program
    : moduleDecl+ EOF
    ;

/**
 * Module declaration defines a namespace for related code.
 * 
 * @ai:naming-convention Use PascalCase for module names.
 * Names should be nouns describing the domain (e.g., UserAuthentication, DataProcessing).
 * 
 * Example:
 * /// This module handles user authentication and session management
 * /// @ai:security-reviewed
 * module UserAuthentication:
 *     // module contents
 */
moduleDecl
    : MODULE identifier COLON INDENT (structDecl | enumDecl | fnDecl | constDecl)* DEDENT
    ;

/**
 * Struct declaration defines a composite data type.
 * 
 * @ai:naming-convention Use PascalCase for struct names.
 * Names should be nouns describing the entity (e.g., User, ConfigSettings).
 * 
 * @ai:best-practice Keep structs focused with a clear purpose.
 * Prefer immutable fields where possible.
 * 
 * Example:
 * /// Represents a user in the system
 * /// @ai:validated
 * struct User:
 *     id: string
 *     name: string
 *     email: string
 */
structDecl
    : STRUCT identifier COLON INDENT fieldDecl* DEDENT
    ;

/**
 * Field declaration within a struct.
 * 
 * @ai:naming-convention Use camelCase for field names.
 * Names should clearly describe the purpose of the field.
 * 
 * @ai:best-practice Include a type for every field.
 * Use Option<T> for fields that may be absent rather than null.
 * 
 * Example:
 * /// User's unique identifier
 * id: string
 * 
 * /// Optional user profile picture
 * profilePicture: Option<string> = None
 */
fieldDecl
    : identifier COLON type (ASSIGN expression)?
    ;

/**
 * Enum declaration defines a type with a fixed set of variants.
 * 
 * @ai:naming-convention Use PascalCase for enum names and variants.
 * Enum names should be singular nouns (e.g., Status, UserRole).
 * 
 * @ai:best-practice Use enums for representing a fixed set of options.
 * Consider using variant data for related information.
 * 
 * Example:
 * /// Represents the status of an order
 * /// @ai:exhaustive-check
 * enum OrderStatus:
 *     Pending
 *     Processing
 *     Shipped(TrackingInfo)
 *     Delivered
 *     Cancelled(string)
 */
enumDecl
    : ENUM identifier COLON INDENT enumVariant* DEDENT
    ;

/**
 * Enum variant declaration.
 * 
 * @ai:naming-convention Use PascalCase for variant names.
 * For variants with data, use descriptive names for the data types.
 * 
 * Example:
 * /// Order has been shipped with tracking information
 * Shipped(TrackingInfo)
 * 
 * /// Order was cancelled with a reason
 * Cancelled(string)
 */
enumVariant
    : identifier (LPAREN type (COMMA type)* RPAREN)?
    ;

/**
 * Function declaration.
 * 
 * @ai:naming-convention Use camelCase for function names.
 * Function names should be verbs or verb phrases describing the action.
 * 
 * @ai:best-practice Include return type annotations even when returning void.
 * Group related parameters, limit parameter count (<= 5 recommended).
 * 
 * Example:
 * /// Authenticates a user and returns a session token
 * /// @ai:security-critical
 * fn authenticateUser(username: string, password: string) -> Result<string, AuthError>:
 *     // function body
 */
fnDecl
    : FN identifier LPAREN paramList? RPAREN (ARROW type)? COLON INDENT statement* DEDENT
    ;

/**
 * Parameter list for function declarations.
 * 
 * @ai:best-practice Keep parameter lists short and focused.
 * Use structs to group related parameters if the list gets too long.
 * 
 * Example:
 * createUser(name: string, email: string, role: UserRole)
 * 
 * // Preferred for many parameters:
 * createUser(userData: UserCreationData)
 */
paramList
    : parameter (COMMA parameter)*
    ;

/**
 * Individual parameter declaration.
 * 
 * @ai:naming-convention Use camelCase for parameter names.
 * Names should clearly describe the parameter's purpose.
 * 
 * @ai:best-practice Always include type annotations.
 * For optional parameters, use Option<T> rather than nullable types.
 * 
 * Example:
 * userId: string
 * options: Option<UserOptions> = None
 */
parameter
    : identifier COLON type
    ;

/**
 * Constant declaration.
 * 
 * @ai:naming-convention Use UPPER_SNAKE_CASE for constants.
 * Names should describe the value's purpose.
 * 
 * @ai:best-practice Use constants for fixed values that won't change.
 * Include type annotations for clarity.
 * 
 * Example:
 * /// Maximum number of login attempts before account lockout
 * /// @ai:security-parameter
 * const MAX_LOGIN_ATTEMPTS: int = 5
 */
constDecl
    : CONST identifier COLON type ASSIGN expression
    ;

/**
 * Type definition.
 * 
 * @ai:best-practice Use the most specific type applicable.
 * Prefer Option<T> over nullable types, and Result<T,E> for fallible operations.
 * 
 * Examples:
 * int                           // Simple primitive type
 * User                          // User-defined type
 * Option<User>                  // Optional user (preferred over nullable)
 * Result<User, DatabaseError>   // User or error from database operation
 * [string]                      // Array of strings
 */
type
    : PRIMITIVE_TYPE                                    # primitiveType
    | identifier                                        # userDefinedType
    | OPTION LESS_THAN type GREATER_THAN                # optionType
    | RESULT LESS_THAN type COMMA type GREATER_THAN     # resultType
    | LBRACKET type RBRACKET                           # arrayType
    ;

/**
 * Statement definition.
 * 
 * @ai:best-practice Keep statements focused and simple.
 * Prefer immutable variables (constants) where possible.
 * Use structured control flow rather than complex expressions.
 */
statement
    : variableDecl
    | assignmentStmt
    | returnStmt
    | ifStmt
    | forStmt
    | whileStmt
    | expressionStmt
    ;

/**
 * Variable declaration.
 * 
 * @ai:naming-convention Use camelCase for variable names.
 * Names should clearly describe the variable's purpose.
 * 
 * @ai:best-practice Include type annotations for clarity.
 * Initialize variables at declaration when possible.
 * 
 * Example:
 * /// User's authentication token
 * let authToken: string = generateToken(userId)
 * 
 * /// Optional user preferences
 * let preferences: Option<UserPreferences> = fetchPreferences(userId)
 */
variableDecl
    : LET identifier COLON type (ASSIGN expression)? 
    ;

/**
 * Assignment statement.
 * 
 * @ai:best-practice Minimize reassignment of variables.
 * Prefer let declarations with initialization over separate assignment.
 * 
 * Example:
 * counter = counter + 1
 * user.name = newName
 */
assignmentStmt
    : expression ASSIGN expression
    ;

/**
 * Return statement.
 * 
 * @ai:best-practice Ensure return types match function declaration.
 * For void functions, use return without an expression.
 * Use Result<T,E> for functions that can fail.
 * 
 * Example:
 * return user                             // Return a value
 * return Result.Ok(user)                  // Return success with value
 * return Result.Err(DatabaseError.NotFound) // Return error
 */
returnStmt
    : RETURN expression?
    ;

/**
 * If statement.
 * 
 * @ai:best-practice Keep conditions simple and explicit.
 * Avoid deep nesting; extract complex logic to functions.
 * Consider using match expressions for multi-way conditionals.
 * 
 * Example:
 * /// @ai:branch-coverage
 * if user.isAdmin:
 *     // admin logic
 * else if user.hasPermission(Permission.Edit):
 *     // edit logic
 * else:
 *     // regular user logic
 */
ifStmt
    : IF expression COLON INDENT statement* DEDENT
      (ELSE IF expression COLON INDENT statement* DEDENT)*
      (ELSE COLON INDENT statement* DEDENT)?
    ;

/**
 * For statement for iteration.
 * 
 * @ai:best-practice Use for loops for iterating over collections.
 * Keep loop bodies focused; extract complex logic to functions.
 * 
 * Example:
 * /// Process each user in the list
 * /// @ai:parallelizable
 * for user in users:
 *     processUser(user)
 */
forStmt
    : FOR identifier IN expression COLON INDENT statement* DEDENT
    ;

/**
 * While statement for conditional loops.
 * 
 * @ai:best-practice Include a clear termination condition.
 * Avoid infinite loops; ensure the condition will eventually be false.
 * Consider using a for loop if the number of iterations is known.
 * 
 * Example:
 * /// Retry operation until successful or max attempts reached
 * /// @ai:max-iterations=5
 * while retryCount < MAX_RETRIES and not success:
 *     success = attemptOperation()
 *     retryCount = retryCount + 1
 */
whileStmt
    : WHILE expression COLON INDENT statement* DEDENT
    ;

/**
 * Expression statement.
 * 
 * @ai:best-practice Use expression statements for function calls with side effects.
 * Avoid unused expressions.
 * 
 * Example:
 * logMessage("Operation completed")
 * database.saveUser(user)
 */
expressionStmt
    : expression
    ;

/**
 * Expression definition.
 * 
 * @ai:best-practice Keep expressions simple and focused.
 * Break complex expressions into smaller, named variables.
 * Use parentheses to clarify precedence in complex expressions.
 */
expression
    : primary                                                # primaryExpr
    | LPAREN expression RPAREN                               # parenExpr
    | expression DOT identifier                              # memberAccessExpr
    | identifier LPAREN expressionList? RPAREN               # constructorOrFunctionExpr
    | expression LPAREN expressionList? RPAREN               # methodCallExpr
    | expression LBRACKET expression RBRACKET                # indexExpr
    | op=(PLUS | MINUS | NOT) expression                     # unaryExpr
    | expression op=(MUL | DIV | MOD) expression             # multiplicativeExpr
    | expression op=(PLUS | MINUS) expression                # additiveExpr
    | expression op=(LESS_THAN | LESS_EQUAL | GREATER_THAN | GREATER_EQUAL) expression # relationalExpr
    | expression op=(EQUAL | NOT_EQUAL) expression           # equalityExpr
    | expression AND expression                              # andExpr
    | expression OR expression                               # orExpr
    | <assoc=right> expression QUESTION expression COLON expression # conditionalExpr
    | AWAIT expression                                       # awaitExpr
    ;

/**
 * Expression list for function calls, method calls, and constructors.
 * 
 * @ai:best-practice Use named parameters for clarity in complex function calls.
 * Limit the number of arguments (<= 5 recommended).
 * 
 * Example:
 * createUser("John Doe", "john@example.com", UserRole.Regular)
 * 
 * // Preferred for clarity:
 * createUser(name: "John Doe", email: "john@example.com", role: UserRole.Regular)
 */
expressionList
    : expression (COMMA expression)*
    ;

/**
 * Primary expressions (literals and identifiers).
 * 
 * @ai:best-practice Use appropriate literal types for values.
 * Consider defining named constants for magic numbers.
 */
primary
    : INTEGER_LITERAL                                       # integerLiteral
    | FLOAT_LITERAL                                         # floatLiteral
    | STRING_LITERAL                                        # stringLiteral
    | BOOLEAN_LITERAL                                       # booleanLiteral
    | identifier                                            # identifierLiteral
    | NONE                                                  # noneLiteral
    | LBRACKET (expression (COMMA expression)*)? RBRACKET   # arrayLiteral
    ;

/**
 * Identifier definition.
 * 
 * @ai:naming-convention Follow these conventions:
 * - PascalCase for types, modules, enums (User, AuthModule)
 * - camelCase for variables, functions, fields (userName, calculateTotal)
 * - UPPER_SNAKE_CASE for constants (MAX_RETRY_COUNT)
 * 
 * @ai:best-practice Use clear, descriptive names that convey purpose.
 * Avoid abbreviations unless widely understood.
 */
identifier
    : IDENTIFIER
    ;

// Lexer Rules
/**
 * Keywords and tokens for the Aegis language.
 * These define the fundamental building blocks of the language syntax.
 */
MODULE: 'module';
STRUCT: 'struct';
ENUM: 'enum';
FN: 'fn';
CONST: 'const';
LET: 'let';
RETURN: 'return';
IF: 'if';
ELSE: 'else';
FOR: 'for';
IN: 'in';
WHILE: 'while';
AWAIT: 'await';
OPTION: 'Option';
RESULT: 'Result';
NONE: 'None';
AND: 'and';
OR: 'or';

/**
 * Primitive types in Aegis.
 * 
 * @ai:best-practice Use the most specific type applicable:
 * - int: For integer values
 * - float: For decimal values
 * - bool: For true/false values
 * - string: For text values
 */
PRIMITIVE_TYPE: 'int' | 'float' | 'bool' | 'string';
BOOLEAN_LITERAL: 'true' | 'false';

/**
 * Punctuation and operators.
 * These define the syntax for expressions, statements, and declarations.
 */
COLON: ':';
SEMICOLON: ';';
COMMA: ',';
DOT: '.';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACKET: '[';
RBRACKET: ']';
ARROW: '->';
ASSIGN: '=';
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
MOD: '%';
NOT: '!';
EQUAL: '==';
NOT_EQUAL: '!=';
LESS_THAN: '<';
LESS_EQUAL: '<=';
GREATER_THAN: '>';
GREATER_EQUAL: '>=';
QUESTION: '?';

/**
 * Special tokens for indentation-based syntax.
 * These are inserted by the preprocessor to handle Python-like indentation.
 */
INDENT: 'INDENT'; // Will be inserted by preprocessor
DEDENT: 'DEDENT'; // Will be inserted by preprocessor

/**
 * Identifier pattern.
 * 
 * @ai:naming-convention Follow these conventions:
 * - PascalCase for types, modules, enums (User, AuthModule)
 * - camelCase for variables, functions, fields (userName, calculateTotal)
 * - UPPER_SNAKE_CASE for constants (MAX_RETRY_COUNT)
 */
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

/**
 * Literal patterns for integers, floats, and strings.
 */
INTEGER_LITERAL: [0-9]+;
FLOAT_LITERAL: [0-9]+ '.' [0-9]+;
STRING_LITERAL: '"' (~["\r\n] | '\\"')* '"';

/**
 * Whitespace and comments.
 * These are skipped during parsing.
 * 
 * @ai:documentation-convention Use '#' for single-line comments.
 * For documentation comments, use the following format:
 * /// This is a documentation comment
 * /// @ai:tag Additional metadata
 */
WHITESPACE: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;

/**
 * Documentation comment rule (new addition).
 * This allows for structured documentation with special AI tags.
 * 
 * Example:
 * /// This function authenticates a user
 * /// @ai:security-reviewed
 * /// @ai:performance-critical
 */
DOC_COMMENT: '///' ~[\r\n]* -> channel(HIDDEN); 