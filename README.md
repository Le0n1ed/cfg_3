# 1 ЭТАП
# Запуск: python assembler.py test.asm intermediate.txt --test
# 2 ЭТАП
# Запуск: python assembler.py test.asm test.bin
# python assembler.py test.asm test.bin --test
# 3 ЭТАП
# Запуск: python assembler.py correct_test.asm correct_test.bin --test
# python interpreter.py correct_test.bin memory_dump.csv 0 100
