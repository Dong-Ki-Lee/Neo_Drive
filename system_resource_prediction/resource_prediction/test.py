input_list = [8, 7, 3, 7, 7, 7, 5, 10, 8, 6, 7, 9, 8, 7]

for i in range(0, 14):
    diff = input_list[i+7] - input_list[i]
    input_list.append(input_list[i+7] + diff)

print(input_list)
