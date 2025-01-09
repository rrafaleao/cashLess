# Dicionarios são valores chaves pares, não ordenado e mutável

mydict = {
"name":"Rafael",
"age":"17",
"city": "Novohamburgo"
}

# outro jeito de criar um dicionario é com a função dict, desse modo:
mydict2 = dict(name="Luisa", age="17", city="NovoHamburgo")

#para acessar um valor especifico:

namevalue = mydict["name"]

#Para adicionar algo ao dicionario é feito dessa forma:

mydict["email"] = "rafa@123.com"

# para remover um item do dicionario, tem mais de um jeito:

del mydict["email"]
mydict.pop("age")

# Para checar se tem algo dentro dicionario:

if "name" in mydict:
    print(mydict["name"])
else:
    print("naoooo")

try:
    print(mydict["name"])
except:
    print("erro")


# Para fazer um loop com o dicionario, existem variás opções:

# Para passar pelas "chaves"
for key in mydict.keys():
    print(key)

# Para printar os valores
for value in mydict.values():
    print(value)

#Para printar os dois:

for keys, values in mydict.items():
    print(keys, values)

#para fazer uma copia de um dicionario:

mydict_copy = mydict.copy()

# para juntar dois dicionarios:

my_dict = {"name" : "rafaek", "age" : "27", "email":"rafa@xyz.com"}
my_dict2 = dict(name="mariana", age="29", city="newyork")

my_dict.update(my_dict2)
print(my_dict)


print(mydict)