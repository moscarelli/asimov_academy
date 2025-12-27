# Ollama Model Evaluation Results

## Health Check Results
| Model | Step | Time (s) | Error | Response |
|-------|------|----------|-------|----------|
| mistral:7b | health | 11.36288070678711 | None |  Hello! How can I assist you today? If you have any questions or need help with  ... |
| llama3:8b | health | 12.974563598632812 | None | Hello! It's nice to meet you. Is there something I can help you with, or would y ... |
| llama2:7b | health | 11.37295937538147 | None | Hello! It's nice to meet you. Is there something I can help you with or would yo ... |
| phi:2.7b | health | 5.782441854476929 | None |  Hello! How can I assist you today?
 ... |
| tinyllama:1.1b | health | 4.5100672245025635 | None | Hi! I'm glad to hear that you found the text helpful. If you have any questions  ... |
| codegemma:7b | health | 13.272487163543701 | None | Hello! 👋 I'm happy to hear from you. How can I assist you today? 😊 ... |

## Code Understanding Results
| Model | Language | Step | Time (s) | Accurate | Error | Response |
|-------|----------|------|----------|---------|-------|----------|
| mistral:7b | Python | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| mistral:7b | Java | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| mistral:7b | C# | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| mistral:7b | JavaScript | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama3:8b | Python | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama3:8b | Java | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama3:8b | C# | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama3:8b | JavaScript | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama2:7b | Python | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama2:7b | Java | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama2:7b | C# | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| llama2:7b | JavaScript | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| phi:2.7b | Python | understand | 22.28358292579651 | False | None |  This code defines a function called "calculate_discount". It takes two paramete ... |
| phi:2.7b | Java | understand | 9.213073015213013 | False | None |  This code is an example of a business transaction. It calculates the amount of  ... |
| phi:2.7b | C# | understand | 13.099635124206543 | False | None |  This code is a simple program that helps customers calculate the discount they  ... |
| phi:2.7b | JavaScript | understand | 17.977898120880127 | False | None |  The code calculates a 10% discount for orders over $100 and offers a 20% discou ... |
| tinyllama:1.1b | Python | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| tinyllama:1.1b | Java | understand | 9.14936900138855 | False | None | That's it! This is a simple C++ program that checks if an order total exceeds th ... |
| tinyllama:1.1b | C# | understand | 5.541102409362793 | False | None | This code is a C# program that checks if the total order amount is greater than  ... |
| tinyllama:1.1b | JavaScript | understand | 7.560256719589233 | False | None | The code "calculateDiscount" takes three arguments: the total amount of a purcha ... |
| codegemma:7b | Python | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| codegemma:7b | Java | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| codegemma:7b | C# | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| codegemma:7b | JavaScript | understand | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |

## Business Rule Extraction Results
| Model | Language | Step | Time (s) | Accurate | Error | Response |
|-------|----------|------|----------|---------|-------|----------|
| phi:2.7b | Python | business | 12.568053722381592 | False | None |  The business rule implemented in this code is that if the order total is over $ ... |
| phi:2.7b | Java | business | 11.267771244049072 | False | None |  The business rule implemented in this code is to offer a 10% discount on orders ... |
| phi:2.7b | C# | business | 8.809818506240845 | False | None |  The business rule implemented in this code is that if the order total is greate ... |
| phi:2.7b | JavaScript | business | 17.45306134223938 | False | None |  The business rule implemented in this code is to give a 10% discount to loyal c ... |

## Final Comprehensive Test Results
| Model | Language | Step | Time (s) | Accurate | Error | Response |
|-------|----------|------|----------|---------|-------|----------|
| phi:2.7b |  | final-health | 2.75313663482666 |  | None |  Hello! How can I assist you today?
 ... |
| phi:2.7b | Python | final-understand | 19.424784898757935 | False | None |  This code defines a function called "calculate_discount", which takes two argum ... |
| phi:2.7b | Java | final-understand | 13.328746795654297 | False | None |  Hi there! This code is a Java program that calculates the discount for an order ... |
| phi:2.7b | C# | final-understand | 24.301735162734985 | False | None |  This code implements a DiscountRule class that calculates the discount on an or ... |
| phi:2.7b | JavaScript | final-understand | 20.385849952697754 | False | None |  This code defines a function called `calculateDiscount` that takes two argument ... |
| phi:2.7b | Python | final-business | 18.127536296844482 | False | None |  The business rule implemented in this code is to apply a 10% discount on orders ... |
| phi:2.7b | Java | final-business | None | False | HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=30) | None ... |
| phi:2.7b | C# | final-business | 9.661137819290161 | False | None |  The business rule implemented in this code is to offer a 10% discount on the or ... |
| phi:2.7b | JavaScript | final-business | 10.980433702468872 | False | None |  The business rule implemented in this code is that customers who spend over 100 ... |