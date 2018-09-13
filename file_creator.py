#!env/bin/python3
import os

def main_function():
    editable_file_name = 'yo.txt'
    editable_file_dir = '/home/debashis/work/python-learning/'  #test directory
    
    temp_string = ""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    
    try:
        file_path = os.path.join(base_dir, "xa.txt")
    
        with open(file_path, 'r') as ll:
            lines = ll.read()
            temp_string += lines
    except ValueError as err1:
        print(err1)
        
    try:
        from string import Template
        new_str = Template(temp_string).substitute(x = 'heeeeeeeeeeeeeeeee')
        
        #print(new_str)
        
        if(not os.path.isfile(os.path.join(editable_file_dir, editable_file_name))):
            f= open(editable_file_name,"w+")    #new file create
            f.write(new_str)
        else:
            print('noo file')
        
        try:
            import shlex, subprocess
            
            out_list = list()
            arg = shlex.split("systemctl restart nginx.service")
            proc = subprocess.Popen(arg, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            out, err = proc.communicate()
            if out:
                out_list = out.strip(" \n").split("\n")
            return out_list, err
        except ValueError as err2:
            print(err2)
        
    except ValueError as err3:
        print(err3)


if __name__ == "__main__":
    main_function()
