import codecs

filepath = r'c:\Users\andre\Desktop\Programacion\Curso y Practica de Python\ProyectoApuestas\static\js\dashboard.js'

with codecs.open(filepath, 'r', 'utf-8') as f:
    data = f.read()

# Bad spaces in HTML
data = data.replace('< div ', '<div ')
data = data.replace('</div >', '</div>')
data = data.replace('< tr >', '<tr>')
data = data.replace('</tr >', '</tr>')
data = data.replace('< tr class', '<tr class')
data = data.replace('" >', '">')

# Bad spaces in template literals text
data = data.replace('% `', '%`')
data = data.replace('} v`', '}v`')
data = data.replace('+ ${', '+${')
data = data.replace('- ${', '-${')
data = data.replace('} `', '}`')

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(data)
