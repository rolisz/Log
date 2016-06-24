from bs4 import BeautifulSoup

f = open("./Facebook/messages.htm")
doc = f.read()
soup = BeautifulSoup(doc, 'html.parser')
pretty = soup.prettify()
f = open("Facebook/cleaned.html", "w")
f.write(pretty)
f.close()
