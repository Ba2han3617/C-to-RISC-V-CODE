# C to RISC-V Compiler

## Overview

This project is a **C to RISC-V Compiler**. It takes C source code as input and transforms it into RISC-V assembly code. This tool is useful for learning about compiler construction, experimenting with RISC-V assembly, and running C programs on RISC-V hardware or simulators.

## Features

- **C Language Support:** Compile standard C code to RISC-V assembly.
- **RISC-V Output:** Generates assembly compatible with RISC-V tools and emulators.
- **Command-line Interface:** Simple CLI for compiling files.
- **Educational:** Useful for teaching and learning about compilers and computer architecture.

## Getting Started

### Prerequisites

- (Optional) RISC-V toolchain for assembling and running the output.
- (Optional) RISC-V emulator (like Spike or QEMU) or hardware.

### Building

Clone the repository and build the compiler (update the commands as needed for your environment):

```sh
git clone https://github.com/yourusername/c-to-riscv-compiler.git
cd c-to-riscv-compiler
make
```

### Usage

To compile a C file to RISC-V assembly:

```sh
./c2riscv input.c -o output.s
```

- `input.c`: Input C source file.
- `output.s`: Output RISC-V assembly file.

To assemble and run the output (if you have the RISC-V toolchain):

```sh
riscv64-unknown-elf-gcc -o output output.s
spike pk output
```

## Example

Given the following C code (`example.c`):

```c
#include <stdio.h>

int main() {
    printf("Hello, RISC-V!\n");
    return 0;
}
```

Compile it:

```sh
./c2riscv example.c -o example.s
```

## Contributing

Contributions are welcome! Please fork the repository and open a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- RISC-V Foundation
- Open source compiler communities
