# Aegis - AI Control & Guidance

Aegis is an AI-optimized, high-performance, and type-safe programming language designed for deterministic, error-free code generation. Built on LLVM and WebAssembly, Aegis empowers developers to create secure and scalable applications with a focus on clarity and efficiency.

## 🎓 Why isn't this just another language?

- Deterministic Sytax: Indentation-based with no hidden conversions.
- Minimal Ambiguity:
- Easy to Parse: Tokenized
- Strong Typing: No null by default
- Strict: Forces code correctness to help AI produce fewer errors.
- Compiled, memory-safe, and type-safe by default.
- Scalable & Modular: Support modules, package manager, and a standard library.
- Compilation Targets: LLVM IR, WebAssembly, and native binaries.
- **Made for AI:** Straightforward scoping, no tricky corner cases, and minimal variance.

## 🔥 Features

- **AI-Optimized Code Generation:**  
  Leverage AI-driven tools to automatically generate, validate, and optimize code.

- **Strong Type Safety:**  
  Aegis enforces strict typing with no null values, ensuring predictable behavior.

- **High Performance:**  
  Utilizes LLVM for native compilation and supports WebAssembly for portable, browser-based execution.

- **Built-in Standard Library:**  
  Includes robust functionality for arithmetic, string manipulation, file I/O, networking, and date/time operations.

- **Modular Design & Package Management:**  
  Easily structure your projects with modules and manage dependencies with Aegis’ integrated package manager.

## Installation

Clone the repository and run the installation script to set up Aegis on your system:

```bash
git clone https://github.com/your-username/aegis.git
cd aegis
./install.sh
```

Note: Ensure you have LLVM, Clang, and Python 3 installed on your system.

## Usage

### Compiling Aegis Code

To compile an Aegis source file (e.g., example.ae), run:

```bash
python compiler/aegis_compiler.py examples/example.ae
```

This will:
    - Tokenize and parse your source code.
    - Perform semantic analysis and type checking.
    - Generate LLVM IR.
    - Optionally run JIT compilation to execute your code.

### AI-Driven Code Generation

Aegis includes an AI code generator for scaffolding SaaS modules and enterprise projects. To generate sample code:

```bash
python compiler/aegis_ai_generator.py
```

This script will output AI-generated Aegis code that you can further modify.

### Example

Below is a simple Aegis example:

```bash
module UserSystem:

    struct User:
        name: string
        age: int

    fn get_user(name: string) -> User:
        return User(name, 25)
```

Save this as examples/example.ae and compile it using the instructions above.

## 📝 Contributing

We welcome contributions to Aegis! Please check out our CONTRIBUTING.md for guidelines on how to get started. In general, pull requests are welcome! However, please open an issue for major changes to start a discussion.

## Roadmap

- [] Establish documentation 📚.
- [] Enhanced AI Assistance: Further integration of AI for code refactoring and error correction.
- [] Expanded Standard Library: Additional modules for advanced networking, cryptography, and cloud-native development.
- [] Tooling & IDE Support: Developing plugins and an online playground for real-time code generation and testing.
- [] Performance Optimization: Continuous improvements to the LLVM backend and WebAssembly support.

## 📃 License

Aegis is open source under the [MIT](https://github.com/AurixLang/Aurix/blob/main/LICENSE) License.

---
## 🗨️ Contact Us

⭐ Star us on GitHub — it motivates us a lot!

[![Share](https://img.shields.io/badge/share-000000?logo=x&logoColor=white)](https://x.com/intent/tweet?text=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/Abblix/Oidc.Server%20%23OpenIDConnect%20%23Security%20%23Authentication)
[![Share](https://img.shields.io/badge/share-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/Abblix/Oidc.Server)
[![Share](https://img.shields.io/badge/share-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/Abblix/Oidc.Server)
[![Share](https://img.shields.io/badge/share-FF4500?logo=reddit&logoColor=white)](https://www.reddit.com/submit?title=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/Abblix/Oidc.Server)
[![Share](https://img.shields.io/badge/share-0088CC?logo=telegram&logoColor=white)](https://t.me/share/url?url=https://github.com/Abblix/Oidc.Server&text=Check%20out%20this%20project%20on%20GitHub)

Join our community on Discord and follow us on Twitter for the latest updates and discussions.

Happy coding with Aegis!