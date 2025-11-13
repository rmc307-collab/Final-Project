try:
    import julia 
    print ("Successfully imported julia module")
    print (f"Julia module file: {julia.__file__}")
    print (f"Julia module version: {julia.__version__}")
except ImportError as e:
    print (f"Still getting import error: {e}")
except Exception as e:
    print (f"Some other error occurred: {e}")


import julia 
jl = julia.Julia(compiled_modules=False)
from julia import Main

# Test that Julia is working
result = Main.eval("2+3")
print (f"Result: {result}")

# Array operations
Main.eval("arr = [1, 2, 3, 4, 5]") 
sum_result = Main.eval("sum(arr)") 
print(f"✓ Array sum: {sum_result}")
# Function definition
Main.eval("""
function test_function(x, y)
    return x^2 + y^2
end
""")
func_result = Main.eval("test_function(3, 4)") 
print(f"✓ Custom function: 32 + 42 = {func_result}") 
print("\n🎉 Julia is working without warnings!")