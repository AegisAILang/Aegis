
class StandardLibrary:
    """Defines the core standard library functions for AegisLang."""

    def __init__(self):
        self.library = {}

    def register_builtin_functions(self):
        """Registers core built-in functions."""
        self.library["print"] = {
            "params": [("message", "string")],
            "return": "void",
            "llvm_ir": self.generate_print_function(),
        }

        self.library["add"] = {
            "params": [("a", "int"), ("b", "int")],
            "return": "int",
            "llvm_ir": self.generate_add_function(),
        }

    def generate_print_function(self):
        """Generates LLVM IR for a print function."""
        return """
        declare void @puts(i8*)
        
        define void @print(i8* %message) {
            call void @puts(i8* %message)
            ret void
        }
        """

    def generate_add_function(self):
        """Generates LLVM IR for an integer addition function."""
        return """
        define i64 @add(i64 %a, i64 %b) {
            %sum = add i64 %a, %b
            ret i64 %sum
        }
        """
    
class ExtendedStandardLibrary(StandardLibrary):
    """Expands the standard library with more built-in functions."""

    def register_extended_functions(self):
        """Registers additional utility functions."""

        self.library["subtract"] = {
            "params": [("a", "int"), ("b", "int")],
            "return": "int",
            "llvm_ir": self.generate_subtract_function(),
        }

        self.library["multiply"] = {
            "params": [("a", "int"), ("b", "int")],
            "return": "int",
            "llvm_ir": self.generate_multiply_function(),
        }

        self.library["divide"] = {
            "params": [("a", "int"), ("b", "int")],
            "return": "Result<int, string>",
            "llvm_ir": self.generate_divide_function(),
        }

        self.library["length"] = {
            "params": [("s", "string")],
            "return": "int",
            "llvm_ir": self.generate_length_function(),
        }

        self.library["concat"] = {
            "params": [("s1", "string"), ("s2", "string")],
            "return": "string",
            "llvm_ir": self.generate_concat_function(),
        }

    def generate_subtract_function(self):
        """Generates LLVM IR for subtraction."""
        return """
        define i64 @subtract(i64 %a, i64 %b) {
            %diff = sub i64 %a, %b
            ret i64 %diff
        }
        """

    def generate_multiply_function(self):
        """Generates LLVM IR for multiplication."""
        return """
        define i64 @multiply(i64 %a, i64 %b) {
            %product = mul i64 %a, %b
            ret i64 %product
        }
        """

    def generate_divide_function(self):
        """Generates LLVM IR for safe division (returns Result<int, string>)."""
        return """
        define i64 @divide(i64 %a, i64 %b) {
            %is_zero = icmp eq i64 %b, 0
            br i1 %is_zero, label %error, label %continue

        error:
            ret i64 -1  ; Use a special value to indicate error (to be replaced with proper error handling)
        
        continue:
            %quotient = sdiv i64 %a, %b
            ret i64 %quotient
        }
        """

    def generate_length_function(self):
        """Generates LLVM IR for string length calculation."""
        return """
        declare i64 @strlen(i8*)

        define i64 @length(i8* %s) {
            %len = call i64 @strlen(i8* %s)
            ret i64 %len
        }
        """

    def generate_concat_function(self):
        """Generates LLVM IR for string concatenation."""
        return """
        declare i8* @strcat(i8*, i8*)

        define i8* @concat(i8* %s1, i8* %s2) {
            %result = call i8* @strcat(i8* %s1, i8* %s2)
            ret i8* %result
        }
        """

class FullStandardLibrary(ExtendedStandardLibrary):
    """Further expands the standard library with file I/O, networking, and date/time utilities."""

    def register_advanced_functions(self):
        """Registers file I/O, networking, and date/time functions."""

        # File I/O Functions
        self.library["read_file"] = {
            "params": [("filename", "string")],
            "return": "string",
            "llvm_ir": self.generate_read_file_function(),
        }

        self.library["write_file"] = {
            "params": [("filename", "string"), ("content", "string")],
            "return": "bool",
            "llvm_ir": self.generate_write_file_function(),
        }

        # HTTP Networking Functions
        self.library["http_get"] = {
            "params": [("url", "string")],
            "return": "string",
            "llvm_ir": self.generate_http_get_function(),
        }

        self.library["http_post"] = {
            "params": [("url", "string"), ("data", "string")],
            "return": "string",
            "llvm_ir": self.generate_http_post_function(),
        }

        # Date/Time Functions
        self.library["current_timestamp"] = {
            "params": [],
            "return": "int",
            "llvm_ir": self.generate_current_timestamp_function(),
        }

        self.library["format_date"] = {
            "params": [("timestamp", "int"), ("format", "string")],
            "return": "string",
            "llvm_ir": self.generate_format_date_function(),
        }

    def generate_read_file_function(self):
        """Generates LLVM IR for reading a file."""
        return """
        declare i8* @read_file(i8*)
        
        define i8* @read_file_wrapper(i8* %filename) {
            %content = call i8* @read_file(i8* %filename)
            ret i8* %content
        }
        """

    def generate_write_file_function(self):
        """Generates LLVM IR for writing to a file."""
        return """
        declare i1 @write_file(i8*, i8*)
        
        define i1 @write_file_wrapper(i8* %filename, i8* %content) {
            %success = call i1 @write_file(i8* %filename, i8* %content)
            ret i1 %success
        }
        """

    def generate_http_get_function(self):
        """Generates LLVM IR for HTTP GET requests."""
        return """
        declare i8* @http_get(i8*)
        
        define i8* @http_get_wrapper(i8* %url) {
            %response = call i8* @http_get(i8* %url)
            ret i8* %response
        }
        """

    def generate_http_post_function(self):
        """Generates LLVM IR for HTTP POST requests."""
        return """
        declare i8* @http_post(i8*, i8*)
        
        define i8* @http_post_wrapper(i8* %url, i8* %data) {
            %response = call i8* @http_post(i8* %url, i8* %data)
            ret i8* %response
        }
        """

    def generate_current_timestamp_function(self):
        """Generates LLVM IR for getting the current timestamp."""
        return """
        declare i64 @current_timestamp()
        
        define i64 @current_timestamp_wrapper() {
            %time = call i64 @current_timestamp()
            ret i64 %time
        }
        """

    def generate_format_date_function(self):
        """Generates LLVM IR for formatting timestamps."""
        return """
        declare i8* @format_date(i64, i8*)
        
        define i8* @format_date_wrapper(i64 %timestamp, i8* %format) {
            %formatted_date = call i8* @format_date(i64 %timestamp, i8* %format)
            ret i8* %formatted_date
        }
        """
# Example usage:
if __name__ == "__main__":
    lib = FullStandardLibrary()
    lib.register_builtin_functions()
    lib.register_extended_functions()
    lib.register_advanced_functions()
    for func, details in lib.library.items():
        print(func, details["params"], details["return"])
