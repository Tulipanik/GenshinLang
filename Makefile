INPUT=input.gl
LLVM_IR=output.ll
OBJ=output.o
EXEC=output

all: $(EXEC)

$(LLVM_IR): main.py $(INPUT)
	python3 main.py $(INPUT)

$(OBJ): $(LLVM_IR)
	llc -filetype=obj $(LLVM_IR) -o $(OBJ)

$(EXEC): $(OBJ)
	clang $(OBJ) -o $(EXEC)

run: $(EXEC)
	./$(EXEC)

clean:
	clear
	rm -f $(LLVM_IR) $(OBJ) $(EXEC)
