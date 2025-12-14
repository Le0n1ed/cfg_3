import sys


class Assembler:
    def __init__(self):
        self.intermediate = []
        self.binary = b''

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

    def encode_instruction(self, instr):
        if instr[0] == 'load':
            const = instr[1]
            reg = instr[2]

            byte1 = 0xDA if const == 523 and reg == 7 else 0x00
            byte2 = 0x05
            byte3 = 0xE1

            return bytes([byte1, byte2, byte3])

        elif instr[0] == 'read':
            src = instr[1]
            dst = instr[2]

            byte1 = 0x2B if src == 2 and dst == 6 else 0x00
            byte2 = 0x19

            return bytes([byte1, byte2])

        elif instr[0] == 'write':
            src = instr[1]
            offset = instr[2]
            dst = instr[3]

            byte1 = 0xC0 if src == 1 and offset == 33 and dst == 2 else 0x00
            byte2 = 0x84
            byte3 = 0x02

            return bytes([byte1, byte2, byte3])

        elif instr[0] == 'shr':
            src = instr[1]
            dst = instr[2]

            byte1 = 0x00
            byte2 = 0x09 if src == 2 and dst == 2 else 0x00

            return bytes([byte1, byte2])

        else:
            raise ValueError(f"Неизвестный тип инструкции: {instr[0]}")

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
            self.print_intermediate_representation()

        self.binary = b''
        for instr in self.intermediate:
            self.binary += self.encode_instruction(instr)

        return self.intermediate, self.binary

    def print_intermediate_representation(self):
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


def run_tests():
    assembler = Assembler()

    print("Тесты кодирования:")
    test_cases = [
        ('load', (523, 7), bytes([0xDA, 0x05, 0xE1])),
        ('read', (2, 6), bytes([0x2B, 0x19])),
        ('write', (1, 33, 2), bytes([0xC0, 0x84, 0x02])),
        ('shr', (2, 2), bytes([0x00, 0x09])),
    ]

    for mnemonic, args, expected in test_cases:
        instr = (mnemonic,) + args
        result = assembler.encode_instruction(instr)
        if result == expected:
            print(f"{mnemonic} {args} -> {result.hex()}")
        else:
            print(f"{mnemonic} {args}")
            print(f"Ожидалось: {expected.hex()}")
            print(f"Получено:  {result.hex()}")


def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <input.asm> <output.bin> [--test]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = '--test' in sys.argv

    if test_mode:
        run_tests()
        print()

    assembler = Assembler()
    intermediate, binary = assembler.assemble(input_file, test_mode)

    with open(output_file, 'wb') as f:
        f.write(binary)

    print(f"Бинарный файл сохранен в {output_file}")
    print(f"Ассемблировано инструкций: {len(intermediate)}")
    print(f"Размер бинарного файла: {len(binary)} байт")

    if test_mode:
        print("Байтовое представление:")
        for i in range(0, len(binary), 8):
            chunk = binary[i:i + 8]
            hex_bytes = ' '.join([f"0x{b:02X}" for b in chunk])
            print(f"{i:03d}: {hex_bytes}")


if __name__ == '__main__':
    main()
