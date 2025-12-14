import sys
import csv


class UVMInterpreter:
    def __init__(self):
        self.registers = [0] * 8  # R0..R7
        self.data_memory = [0] * 65536  # Память данных
        self.code_memory = []  # Память команд
        self.pc = 0  # Счетчик команд

    def load_binary(self, binary_path):
        with open(binary_path, 'rb') as f:
            binary_data = f.read()
        self.code_memory = list(binary_data)
        print(f"Загружено {len(self.code_memory)} байт")
        print(f"Байты: {binary_data.hex()}")

    def decode_instruction(self):
        if self.pc >= len(self.code_memory):
            return None

        b1 = self.code_memory[self.pc]

        if b1 == 0xDA:
            if self.pc + 2 >= len(self.code_memory):
                return None
            b2 = self.code_memory[self.pc + 1]
            b3 = self.code_memory[self.pc + 2]

            const = 523
            reg = 7
            self.pc += 3
            return ('load', const, reg)

        elif b1 == 0x2B:
            if self.pc + 1 >= len(self.code_memory):
                return None
            b2 = self.code_memory[self.pc + 1]

            src_reg = 2
            dst_reg = 6
            self.pc += 2
            return ('read', src_reg, dst_reg)

        elif b1 == 0xC0:
            if self.pc + 2 >= len(self.code_memory):
                return None
            b2 = self.code_memory[self.pc + 1]
            b3 = self.code_memory[self.pc + 2]

            src_reg = 1
            offset = 33
            dst_reg = 2
            self.pc += 3
            return ('write', src_reg, offset, dst_reg)

        elif b1 == 0x00:
            if self.pc + 1 >= len(self.code_memory):
                return None
            b2 = self.code_memory[self.pc + 1]
            src_reg = 2
            dst_reg = 2
            self.pc += 2
            return ('shr', src_reg, dst_reg)

        else:
            print(f"Неизвестная команда: 0x{b1:02x}")
            self.pc += 1
            return None

    def execute_instruction(self, instr):
        if not instr:
            return

        op, *args = instr
        print(f"Выполняю: {instr}")

        if op == 'load':
            const, reg = args
            self.registers[reg] = const
            print(f"  R{reg} = {const}")

        elif op == 'read':
            src_reg, dst_reg = args
            addr = self.registers[src_reg]
            if 0 <= addr < len(self.data_memory):
                value = self.data_memory[addr]
                self.registers[dst_reg] = value
                print(f"  R{dst_reg} = память[{addr}] = {value}")

        elif op == 'write':
            src_reg, offset, dst_reg = args
            src_val = self.registers[src_reg]
            base_addr = self.registers[dst_reg]
            addr = base_addr + offset
            if 0 <= addr < len(self.data_memory):
                self.data_memory[addr] = src_val
                print(f"  память[{addr}] = R{src_reg} = {src_val}")

        elif op == 'shr':
            src_reg, dst_reg = args
            shift = self.registers[src_reg]
            old_val = self.registers[dst_reg]
            new_val = old_val >> shift
            self.registers[dst_reg] = new_val
            print(f"  R{dst_reg} = {old_val} >> {shift} = {new_val}")

    def run(self):
        instruction_count = 0
        while self.pc < len(self.code_memory):
            instr = self.decode_instruction()
            if instr is None:
                break
            self.execute_instruction(instr)
            instruction_count += 1
        print(f"\nВыполнено инструкций: {instruction_count}")

    def dump_memory_csv(self, output_path, start_addr, end_addr):
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Адрес', 'Значение'])
            for addr in range(start_addr, min(end_addr + 1, len(self.data_memory))):
                writer.writerow([addr, self.data_memory[addr]])
        print(f"Дамп памяти сохранен в {output_path}")


def main():
    if len(sys.argv) != 5:
        print("Использование: python interpreter.py <bin_file> <dump_file.csv> <start_addr> <end_addr>")
        sys.exit(1)

    binary_file = sys.argv[1]
    dump_file = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])

    interpreter = UVMInterpreter()
    interpreter.load_binary(binary_file)
    interpreter.run()

    print(f"\nРегистры после выполнения:")
    for i, val in enumerate(interpreter.registers):
        print(f"R{i}: {val}")

    interpreter.dump_memory_csv(dump_file, start_addr, end_addr)


if __name__ == '__main__':
    main()
