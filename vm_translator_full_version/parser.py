from convert import Vm_to_assembly_converter
from os import listdir
from os.path import isfile, join


converter = Vm_to_assembly_converter()

# Initialisation
converter.initialise_memory_segments()



# Getting name of file or directory.
input_name = input("Please enter file name or directory:")
input_type = ''


# Getting name of all files in given directory.
if '\\' in input_name:
    files = [f for f in listdir(input_name) if isfile(join(input_name, f))]
    all_vm_files_names = converter.select_vm_files(files)
    input_type = "directory"
else:
    single_file_name = input_name

    # For looping only one time.
    all_vm_files_names = "1"
    input_type = "file"








# Looping through all files in given directory.
for file_name in all_vm_files_names:

    data = ''

    # Determining of input type (file or directory).
    if input_type == "file":
        file_name = single_file_name
        with open(single_file_name + ".vm", "r") as f:
            data = f.readlines()
    if input_type == "directory":
        with open(file_name + ".vm", "r") as f:
            data = f.readlines()



    # Keeps track of lines in vm files.
    line_number_in_vm_file = -1

    # Going through the each line of .vm file.
    for line1 in data:


        # Checking for function working stack is finished or not.
        if ((line_number_in_vm_file + 1) == (len(data) - 1) ):
            converter.check_next_line_is_empty_line(1)

        # Checking for function working stack is finished or not.
        if line_number_in_vm_file < len(data)  and data[line_number_in_vm_file].strip() == 'return' and len(data[line_number_in_vm_file+1].strip()) == 0:
            converter.check_next_line_is_empty_line(1)
            converter.make_special_labels_to_function()


        # For bypassing of empty lines
        if len(line1.strip()) == 0 :
            line_number_in_vm_file += 1
            continue


        # When there is white space between beginning of line and beginning of text in the line we ignore prespaces in the lines.  for ex:   || _ _ _ _ white space_ _ _ push constant 42
        line = line1
        if line[0] == ' ':
            i = converter.find_letter_starting(line, "bypass_white_space")
            line = line1[i:]


        # Ignoring process of white spaces and comments.
        if ( line[0]!='/' and line[0]!='\n' ):
            if '//' in line:
                final_point_char = '/'
            else:
                final_point_char = '\n'

            # Picking pure vm code (without white spaces or comments)
            final_point = line.index(final_point_char)
            pure_vm_code = line[0:final_point].strip()

            # Find that command is (push or pop) or arithmetic_operation.
            vm_code_type = converter.find_command_type(pure_vm_code)


            # Determine vm commands to assembly codes.
            # With determing types of each vm commands.
            if vm_code_type == "c_call":
                converter.convert_call_operation(pure_vm_code)
            if vm_code_type == "c_function":
                converter.convert_function_operation(pure_vm_code, file_name)
            if vm_code_type == "c_return":
                converter.convert_return_operation(pure_vm_code)
            if vm_code_type == "c_label" or vm_code_type == "c_goto" or vm_code_type == "c_ifGoto":
                converter.convert_branching_operation(pure_vm_code, vm_code_type)
            if vm_code_type == "c_push" or vm_code_type == "c_pop":
                converter.convert_pop__push(pure_vm_code, vm_code_type, file_name)
            if vm_code_type == "c_arithmetic":
                converter.calculate_arithmetic_operation(pure_vm_code)



        line_number_in_vm_file += 1



# Determining assembly file name for keeping all assembly codes.
assembly_file_name = converter.define_assembly_file_name(input_name)

# Writing assembler codes to file_name.asm (same file name with .vm file).
f = open(assembly_file_name + ".asm", "w")
for line in converter.all_assembly_codes:
    f.write(line+'\n')
