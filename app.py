import math
# course = "Python Programming"
# print(course.upper())
# print(course.lower())
# print(course.title())
# x = 1
# x = 1.1
# # x = 1 + 2j  # a + bi
# print(round(3.7))
# print(abs(-2.9))
# print(math.ceil(3.7))
# x = input("x: ")

# y = int(x) + 1
# print(f"x: {x}, y: {y}")
# count = 0
# for i in range(1, 10):
#     if i % 3 == 0:
#         count += 1
#         print(i)
# else:
#     print(f"We have {count} even numbers")


# def greet_user(first_name, last_name):
#     print(f"Hi {first_name} {last_name}!")
#     print("Welcome aboard!")


# greet_user("John", "Smith")
# greet_user(last_name="Smith", first_name="John")

def multiply(*numbers):
    total = 1
    for number in numbers:
        total *= number
    return total


print(multiply(2, 3, 4, 5))
