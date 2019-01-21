class Vm_to_assembly_converter:
    def __init__(self):

        # Arithmetic commands in vm_code.
        self.c_arithmetic_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]

        # This array keeps converted assembly codes.
        self.all_assembly_codes = []


        self.sp = 256

        # For distinguish label names.
        self.label_id = 0

        # For distinguish not_jump_label names.
        self.not_jump_label_id = 0

        # For distinguish function label names.
        self.function_label_id = 0

        # Function return label id.
        self.return_id = 0

        # Function id.
        self.function_id = 0


        # For determing function calling was occured (1 value) or not (0 value)
        self.there_is_function_calling = 0

        # For checking current executing function name.
        self.currently_running_function_name = ''

        # For determing function returning was occured (1 value) or not (0 value)
        self.occurance_of_return = 0

        # Topmost value of stack determines names of currently running function.
        self.function_call_stack = []

        # Checking for function working stack is finished or not.
        self.current_function_working_segment_finished = 0






    # Determine a (recursive or simple) function working segment finished or not. (mean that function return completely (there are multiple returns in working segment of recursive function))
    def check_next_line_is_empty_line(self, result):
        self.current_function_working_segment_finished = result

    # Make unique labels for each function. This prevents collision of same labels (with same name) in the file.
    def make_special_labels_to_function(self):
        if self.there_is_function_calling == 1:

            if len(self.function_call_stack) > 0:
                if self.function_call_stack[-1] != self.currently_running_function_name:
                    self.current_function_working_segment_finished = 0


            if len(self.function_call_stack) == 0:
                self.function_call_stack.append(self.currently_running_function_name)


            if len(self.function_call_stack) > 0  and  self.function_call_stack[-1] != self.currently_running_function_name:
                self.function_call_stack.append(self.currently_running_function_name)


        if self.occurance_of_return == 1:
            if self.current_function_working_segment_finished == 1:
                self.function_call_stack.pop()


                    







    # Initialisation. Make SP pointer 256 (beginning of global stack). And call Sys.init function for start executing vm codes.
    def initialise_memory_segments(self):
        assembly_code = '// Initialisation of stack pointer\n' +\
                        '@256\n' +                              \
                        'D=A\n'+                                \
                        '@0\n' +                                \
                        'M=D\n'

        self.all_assembly_codes.append(assembly_code)
        self.convert_call_operation("call Sys.init 0")




    # Pick only .vm files from given directory.
    def select_vm_files(self, files):
        all_vm_files = []
        for file_name in files:
            start_point = file_name.index('.')
            file_type = file_name[start_point+1:]
            if file_type.strip() == 'vm':
                all_vm_files.append(file_name[:start_point])
        if all_vm_files[0] != "Sys":
            index = all_vm_files.index("Sys")
            temp = all_vm_files[0]
            all_vm_files[index] = temp
            all_vm_files[0] = "Sys"
        return all_vm_files


    # Give name (file_name for single file or folder name for directory) to result assembly file.
    def define_assembly_file_name(self, input):
        assembly_file_name = ''
        if '\\' in input:
            start_point = input.rfind('\\')
            assembly_file_name = input[start_point+1:]
        else:
            assembly_file_name = input
        return assembly_file_name


    # This function will find the what s type of given vm_command (arithmetic, if, label so on..).
    def find_command_type(self, vm_code):
        if "push" in vm_code:
            return "c_push"
        if "pop" in vm_code:
            return "c_pop"
        if vm_code in self.c_arithmetic_commands:
            return "c_arithmetic"
        if "label" in vm_code:
            return "c_label"
        if "if-goto" in vm_code:
            return "c_ifGoto"
        if "goto" in vm_code:
            return "c_goto"
        if "function" in vm_code:
            return "c_function"
        if "call" in vm_code:
            return "c_call"
        if "return" in vm_code:
            return "c_return"
        # will be continue




    # This function finds index of starting text in given line of file.
    # Function is used for two purposes firstly, for ignoring white space in line.
    # Secondly, finding text starting point for determing memory_segment type in -> purpose == "bypass_white_space":
    # vm_command  -> if purpose == "for_determining_memory_segment":
    def find_letter_starting(self, line, purpose):
        # Number of occurences of white spaces.
        i=0

        # Index of second white space in line.
        index = 0

        while True:
            index += 1
            if line[index] == ' ':
                i += 1
            else:
                if purpose == "bypass_white_space":
                    return i
                if purpose == "for_determining_memory_segment":
                    # Stop when find second white space in line.
                    if i == 2:
                        return index



    # Finds type of memory segment which is used in vm code (temp, this, argument and so on).
    def find_memory_segment_type_and_memory_index(self, vm_code, vm_code_type):
        if vm_code_type == "c_push" or vm_code_type == "c_pop":
            starting_point = 0
            if vm_code_type == "c_pop":
                starting_point = 4
            if vm_code_type == "c_push":
                starting_point = 5

            # Finding of memory segment type.
            final_point = self.find_letter_starting(vm_code, "for_determining_memory_segment")
            memory_segment_type = vm_code[starting_point:final_point]

            # Finding of memory index.
            starting_point = final_point
            memory_segment_index = vm_code[starting_point:]

            return {"memory_segment_type":memory_segment_type,
                    "memory_segment_index":memory_segment_index}











    # Convert push and pop commands to respect assembly commands.
    def convert_pop__push(self, vm_code, vm_code_type, file_name):
        info_list = self.find_memory_segment_type_and_memory_index(vm_code, vm_code_type)
        if vm_code_type == "c_push":
            # For constant segment pushes.
            if info_list["memory_segment_type"].strip()=="constant":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +     \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)


            # For local segment pushes.
            if info_list["memory_segment_type"].strip()=="local":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +     \
                              '@1\n'  +     \
                              'A=M+D\n'  +  \
                              'D=M\n'+      \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)


            # For argument segment pushes.
            if info_list["memory_segment_type"].strip()=="argument":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +     \
                              '@2\n'  +     \
                              'A=M+D\n'  +  \
                              'D=M\n'+      \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)



            # For this segment pushes.
            if info_list["memory_segment_type"].strip()=="this":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +     \
                              '@3\n'  +     \
                              'A=M+D\n'  +  \
                              'D=M\n'+      \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)


            # For that segment pushes.
            if info_list["memory_segment_type"].strip()=="that":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +     \
                              '@4\n'  +     \
                              'A=M+D\n'  +  \
                              'D=M\n'+      \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)



            # For static segment pushes.
            if info_list["memory_segment_type"].strip()=="static":
                self.sp += 1
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + file_name + '.' + info_list["memory_segment_index"] + '\n' + \
                              'D=M\n' +     \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)



            # For temp segment pushes.
            if info_list["memory_segment_type"].strip()=="temp":
                self.sp += 1
                current_temp_segment_address = 5 + int(info_list["memory_segment_index"])
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + str(current_temp_segment_address) + '\n' + \
                              'D=M\n' +     \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)


            # For pointer segment pushes.
            if info_list["memory_segment_type"].strip()=="pointer":
                self.sp += 1
                pointer_access_address = 3 + int(info_list["memory_segment_index"])
                assembly_code='//push ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '@' + str(pointer_access_address) + '\n' + \
                              'D=M\n' +     \
                              '@0\n' +      \
                              'A=M\n' +     \
                              'M=D\n' +     \
                              '@0\n' +      \
                              'M=M+1\n'
                self.all_assembly_codes.append(assembly_code)


        if vm_code_type == "c_pop":

            # For local segment pop.
            if info_list["memory_segment_type"].strip()=="local":
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// addr=LCL+index keeps addr in R13 register\n' + \
                              '@1\n' +            \
                              'D=M\n' +           \
                              '@R13\n' +          \
                              'M=D\n' +           \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +           \
                              '@R13\n' +          \
                              'M=M+D\n' +       \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@R13\n' +          \
                              'A=M\n' +           \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)

            # For argument segment pop.
            if info_list["memory_segment_type"].strip()=="argument":
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// addr=ARG+index keeps addr in R13 register\n' + \
                              '@2\n' +            \
                              'D=M\n' +           \
                              '@R13\n' +          \
                              'M=D\n' +           \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +           \
                              '@R13\n' +          \
                              'M=M+D\n' +       \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@R13\n' +          \
                              'A=M\n' +           \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)


            # For this segment pop.
            if info_list["memory_segment_type"].strip()=="this":
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// addr=THIS+index keeps addr in R13 register\n' + \
                              '@3\n' +            \
                              'D=M\n' +           \
                              '@R13\n' +          \
                              'M=D\n' +           \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +           \
                              '@R13\n' +          \
                              'M=M+D\n' +       \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@R13\n' +          \
                              'A=M\n' +           \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)



            # For that segment pop.
            if info_list["memory_segment_type"].strip()=="that":
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// addr=THAT+index keeps addr in R13 register\n' + \
                              '@4\n' +            \
                              'D=M\n' +           \
                              '@R13\n' +          \
                              'M=D\n' +           \
                              '@' + info_list["memory_segment_index"] + '\n' + \
                              'D=A\n' +           \
                              '@R13\n' +          \
                              'M=M+D\n' +       \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@R13\n' +          \
                              'A=M\n' +           \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)


            # For static segment pop.
            if info_list["memory_segment_type"].strip()=="static":
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@' + file_name + '.' + info_list["memory_segment_index"] + '\n' + \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)


            # For temp segment pop.
            if info_list["memory_segment_type"].strip()=="temp":
                current_temp_segment_address = 5 + int(info_list["memory_segment_index"])
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@' +  str(current_temp_segment_address) + '\n' + \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)


            # For pointer segment pop.
            if info_list["memory_segment_type"].strip()=="pointer":
                pointer_access_address = 3 + int(info_list["memory_segment_index"])
                assembly_code='//pop ' + info_list["memory_segment_type"] + ' ' + info_list["memory_segment_index"] + '\n' + \
                              '// sp-- \n' + \
                              '@0\n' +      \
                              'M=M-1\n' +   \
                              '@0\n' +      \
                              'A=M\n'+      \
                              'D=M\n'+      \
                              '// *addr = *sp \n' + \
                              '@' +  str(pointer_access_address) + '\n' + \
                              'M=D\n'
                self.all_assembly_codes.append(assembly_code)



    def calculate_arithmetic_operation(self, arithmetic_operation):
        if arithmetic_operation.strip() == "add":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//add \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13+R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M+D\n'+    \
                          'D=M\n'+      \
                          '// push R13 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'

            self.all_assembly_codes.append(assembly_code)

        if arithmetic_operation.strip() == "sub":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//sub \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13-R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M-D\n'+    \
                          'D=M\n'+      \
                          '// push R13 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'


            self.all_assembly_codes.append(assembly_code)



        if arithmetic_operation.strip() == "neg":
            self.sp -= 1
            self.sp += 1
            assembly_code='//neg \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '// R14=-R14 \n' + \
                          '@R14\n'+     \
                          'M=-D\n'+      \
                          '// push R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'


            self.all_assembly_codes.append(assembly_code)



        if arithmetic_operation.strip() == "eq":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//eq \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13-R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M-D\n'+    \
                          'D=M\n'+      \
                          '@EQUAL' + str(self.label_id) + '\n' +   \
                          'D;JEQ\n' +   \
                          'D=0\n'+      \
                          '// push 0 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '@NOT_EQUAL' + str(self.label_id) + '\n'+   \
                          '0;JMP\n'+    \
                          '(EQUAL' + str(self.label_id) + ')\n'+   \
                          'D=-1\n'+      \
                          '// push -1 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '(NOT_EQUAL' + str(self.label_id) + ')\n'


            self.all_assembly_codes.append(assembly_code)


        if arithmetic_operation.strip() == "gt":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//gt \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13-R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M-D\n'+    \
                          'D=M\n'+      \
                          '@GREATER' + str(self.label_id) + '\n' +   \
                          'D;JGT\n' +   \
                          'D=0\n'+      \
                          '// push 0 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '@NOT_GREATER' + str(self.label_id) + '\n'+   \
                          '0;JMP\n'+    \
                          '(GREATER' + str(self.label_id) + ')\n'+   \
                          'D=-1\n'+      \
                          '// push -1 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '(NOT_GREATER' + str(self.label_id) + ')\n'


            self.all_assembly_codes.append(assembly_code)



        if arithmetic_operation.strip() == "lt":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//lt \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13-R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M-D\n'+    \
                          'D=M\n'+      \
                          '@LESS_THAN' + str(self.label_id) + '\n'  \
                          'D;JLT\n' +   \
                          'D=0\n'+      \
                          '// push 0 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '@NOT_LESS_THAN' + str(self.label_id) + '\n'   \
                          '0;JMP\n'+    \
                          '(LESS_THAN' + str(self.label_id) + ')\n'+   \
                          'D=-1\n'+      \
                          '// push -1 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n' +   \
                          '(NOT_LESS_THAN' + str(self.label_id) + ')\n'


            self.all_assembly_codes.append(assembly_code)



        if arithmetic_operation.strip() == "and":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//and \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13 and R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=M&D\n'+    \
                          'D=M\n'+      \
                          '// push R13 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'


            self.all_assembly_codes.append(assembly_code)


        if arithmetic_operation.strip() == "or":
            self.sp -= 1
            self.sp -= 1
            self.sp += 1
            assembly_code='//or \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R14\n'+     \
                          'M=D\n'+      \
                          '// pop R13 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D\n'+      \
                          '// R13=R13 or R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@R13\n'+     \
                          'M=D|M\n'+    \
                          'D=M\n'+      \
                          '// push R13 \n' + \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'


            self.all_assembly_codes.append(assembly_code)


        if arithmetic_operation.strip() == "not":
            self.sp -= 1
            self.sp += 1
            assembly_code='//not \n' + \
                          '// pop R14 \n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '// R14=!R14 \n' + \
                          '@R14\n'+     \
                          'M=!D\n'+      \
                          '// push R14 \n' + \
                          '@R14\n'+     \
                          'D=M\n'+      \
                          '@0\n' +      \
                          'A=M\n' +     \
                          'M=D\n' +     \
                          '@0\n' +      \
                          'M=M+1\n'


            self.all_assembly_codes.append(assembly_code)
        self.label_id += 1



    # Converts goto, if goto, label to respective opposites in assembly.
    def convert_branching_operation(self, vm_code, vm_code_type):
        if vm_code_type == "c_label":
            label_name = vm_code[5:].strip()
            assembly_code='(' + self.function_call_stack[-1] + '$' + label_name + ')\n'
            self.all_assembly_codes.append(assembly_code)

        if vm_code_type == "c_goto":
            label_name = vm_code[4:].strip()
            assembly_code='// goto branch\n' + \
                          '@' + self.function_call_stack[-1] + '$' + label_name + '\n' +   \
                          '0;JMP\n'
            self.all_assembly_codes.append(assembly_code)

        if vm_code_type == "c_ifGoto":
            label_name = vm_code[7:].strip()
            assembly_code='// pop topmost value, if-goto branch\n' + \
                          '@0\n' +      \
                          'M=M-1\n' +   \
                          '@0\n' +      \
                          'A=M\n'+      \
                          'D=M\n'+      \
                          '@NOT_JUMP_' + str(self.not_jump_label_id) + '\n' + \
                          'D;JEQ\n' + \
                          '@' + self.function_call_stack[-1] + '$' + label_name + '\n' + \
                          '0;JMP\n' + \
                          '(NOT_JUMP_' + str(self.not_jump_label_id) + ')\n'
            self.not_jump_label_id += 1
            self.all_assembly_codes.append(assembly_code)


    def convert_function_operation(self, vm_code, file_name):
            final_point = self.find_letter_starting(vm_code, "for_determining_memory_segment")
            function_name =vm_code[8:final_point].strip()
            local_var_number = vm_code[final_point:].strip()

            # For generating unique labels for functions.
            self.there_is_function_calling = 1
            self.occurance_of_return = 0
            self.currently_running_function_name = function_name
            self.make_special_labels_to_function()

            assembly_code='(' + function_name + ')\n'
            self.all_assembly_codes.append(assembly_code)

            for i in range(0,int(local_var_number)):
                self.convert_pop__push("push constant 0", "c_push", file_name)




    # Convert calling of function to assembly commands.
    def convert_call_operation(self, vm_code):
        final_point = self.find_letter_starting(vm_code, "for_determining_memory_segment")
        function_name =vm_code[4:final_point].strip()
        argument_var_number = vm_code[final_point:].strip()

        assembly_code='// call\n' + \
                      '@' + function_name + '_return' + str(self.return_id) + '\n' + \
                      'D=A\n'+\
                      '@0\n'+\
                      'A=M\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'M=M+1\n'+\
                      '@1\n'+\
                      'D=M\n'+\
                      '@0\n'+\
                      'A=M\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'M=M+1\n'+\
                      '@2\n'+\
                      'D=M\n'+\
                      '@0\n'+\
                      'A=M\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'M=M+1\n'+\
                      '@3\n'+\
                      'D=M\n'+\
                      '@0\n'+\
                      'A=M\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'M=M+1\n'+\
                      '@4\n'+\
                      'D=M\n'+\
                      '@0\n'+\
                      'A=M\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'M=M+1\n'+\
                      '@5\n'+\
                      'D=A\n'+\
                      '@0\n'+\
                      'D=M-D\n'+\
                      '@' + argument_var_number + '\n' +\
                      'D=D-A\n' + \
                      '@2\n'+\
                      'M=D\n'+\
                      '@0\n'+\
                      'D=M\n'+\
                      '@1\n'+\
                      'M=D\n'+\
                      '@' + function_name + '\n' +   \
                      '0;JMP\n' + \
                      '(' + function_name + '_return' + str(self.return_id) + ')\n'

        self.all_assembly_codes.append(assembly_code)
        self.return_id += 1


    # Convert returning of function to assembly commands.
    def convert_return_operation(self, vm_code):
        self.occurance_of_return = 1
        self.there_is_function_calling = 0
        self.make_special_labels_to_function()
        assembly_code='// return\n' + \
                      '@1\n' +        \
                      'D=M\n'+        \
                      '@R14\n' +    \
                      'M=D\n' +       \
                      '@5\n' +        \
                      'D=A\n' +       \
                      '@R14\n' +    \
                      'A=M-D\n' +     \
                      'D=M\n' +       \
                      '@R15\n' +      \
                      'M=D\n' +       \
                      '@0\n' +      \
                      'M=M-1\n' +   \
                      '@0\n' +      \
                      'A=M\n'+      \
                      'D=M\n'+      \
                      '@2\n' +      \
                      'A=M\n' +     \
                      'M=D\n' +     \
                      '@2\n' +      \
                      'D=M\n' +     \
                      '@0\n' +      \
                      'M=D+1\n' +   \
                      '@1\n' +        \
                      'D=A\n' +       \
                      '@R14\n' +    \
                      'A=M-D\n' +     \
                      'D=M\n' +       \
                      '@4\n' +        \
                      'M=D\n' +       \
                      '@2\n' +        \
                      'D=A\n' +       \
                      '@R14\n' +    \
                      'A=M-D\n' +     \
                      'D=M\n' +       \
                      '@3\n' +        \
                      'M=D\n' +       \
                      '@3\n' +        \
                      'D=A\n' +       \
                      '@R14\n' +    \
                      'A=M-D\n' +     \
                      'D=M\n' +       \
                      '@2\n' +        \
                      'M=D\n' +       \
                      '@4\n' +        \
                      'D=A\n' +       \
                      '@R14\n' +    \
                      'A=M-D\n' +     \
                      'D=M\n' +       \
                      '@1\n' +        \
                      'M=D\n' +       \
                      '@R15\n' +      \
                      'A=M\n' +      \
                      '0;JMP\n'

        self.all_assembly_codes.append(assembly_code)
