from jinja2 import Environment, FileSystemLoader
status = {}
f = open("Gemfile.dot")
packaged_count = 0
unpackaged_count = 0
itp_count = 0
total = 0
count = 1
for line in f.readlines():
    details = line.split(",")
    status[details[0]] = [details[1], details[2], details[3], details[4], details[5]]
    if details[5].strip() == "Packaged" or details[5].strip() == "NEW":
        packaged_count += 1
    elif details[5].strip() == "ITP":
        itp_count += 1
    else:
        unpackaged_count += 1
total = packaged_count + itp_count + unpackaged_count
percent_complete = (packaged_count * 100)/total
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('main.html')
render = template.render(locals())
with open("index.html", "w") as file:
    file.write(render)
