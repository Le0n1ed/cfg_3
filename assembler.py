import sys


class Assembler:
    def __init__(self):
        self.intermediate = []

    def parse_instruction(self, line):
        line = line.split(';')[0].strip()
        if not line:
            return None

        parts = line.split()
        if not parts:
            return None

        mnemonic = parts[0].lower()
        args = parts[1:]

        if mnemonic == 'load':
            if len(args) != 2:
                raise ValueError(f"load требует 2 аргумента, получено {len(args)}")
            const = int(args[0])
            addr_reg = int(args[1])
            if not (0 <= const <= 0x3FFF):
                raise ValueError(f"Константа {const} вне диапазона 0..16383")
            if not (0 <= addr_reg <= 7):
                raise ValueError(f"Адрес регистра {addr_reg} вне диапазона 0..7")
            return ('load', const, addr_reg)

        elif mnemonic == 'read':
            if len(args) != 2:
                raise ValueError(f"read требует 2 аргумента, получено {len(args)}")
            src = int(args[0])
            dst = int(args[1])
            if not (0 <= src <= 7) or not (0 <= dst <= 7):
                raise ValueError(f"Адреса регистров вне диапазона 0..7")
            return ('read', src, dst)

        elif mnemonic == 'write':
            if len(args) != 3:
                raise ValueError(f"write требует 3 аргумента, получено {len(args)}")
            src = int(args[0])
            offset = int(args[1])
            dst = int(args[2])
            if not (0 <= src <= 7) or not (0 <= dst <= 7):
                raise ValueError(f"Адреса регистров вне диапазона 0..7")
            if not (0 <= offset <= 63):
                raise ValueError(f"Смещение {offset} вне диапазона 0..63")
            return ('write', src, offset, dst)

        elif mnemonic == 'shr':
            if len(args) != 2:
                raise ValueError(f"shr требует 2 аргумента, получено {len(args)}")
            src = int(args[0])
            dst = int(args[1])
            if not (0 <= src <= 7) or not (0 <= dst <= 7):
                raise ValueError(f"Адреса регистров вне диапазона 0..7")
            return ('shr', src, dst)

        else:
            raise ValueError(f"Неизвестная команда: {mnemonic}")

    def assemble(self, source_path, test_mode=False):
        with open(source_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    instr = self.parse_instruction(line)
                    if instr:
                        self.intermediate.append(instr)
                except ValueError as e:
                    print(f"Ошибка в строке {line_num}: {e}")
                    sys.exit(1)

        if test_mode:
            print("Промежуточное представление:")
            for i, instr in enumerate(self.intermediate):
                fields = []
                if instr[0] == 'load':
                    fields.append(f"A={90}, B={instr[1]}, C={instr[2]}")
                elif instr[0] == 'read':
                    fields.append(f"A={43}, B={instr[1]}, C={instr[2]}")
                elif instr[0] == 'write':
                    fields.append(f"A={64}, B={instr[1]}, C={instr[2]}, D={instr[3]}")
                elif instr[0] == 'shr':
                    fields.append(f"A={0}, B={instr[1]}, C={instr[2]}")
                print(f"{i}: {instr} ({', '.join(fields)})")

        return self.intermediate

    def create_test_program(self):
        test_program = """load 523 7
read 2 6
write 1 33 2
shr 2 2"""
        return test_program


def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <input.asm> <output.txt> [--test]")
        print("\nПример:")
        print("  python assembler.py program.asm intermediate.txt")
        print("  python assembler.py program.asm intermediate.txt --test")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv

    assembler = Assembler()

    intermediate = assembler.assemble(input_file, test_mode)

    with open(output_file, 'w', encoding='utf-8') as f:
        for instr in intermediate:
            f.write(str(instr) + '\n')

    print(f"Промежуточное представление сохранено в {output_file}")
    print(f"Обработано инструкций: {len(intermediate)}")

    if test_mode:
        print("\nТестовая программа из спецификации УВМ:")
        test_prog = assembler.create_test_program()
        print(test_prog)

        print("\nПроверка тестовых инструкций:")
        test_lines = test_prog.split('\n')
        for i, line in enumerate(test_lines):
            try:
                instr = assembler.parse_instruction(line)
                print(f"{i}: {line.strip():20} -> {instr}")
            except Exception as e:
                print(f"{i}: Ошибка: {e}")


if __name__ == '__main__':
    main()
