import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteconfig.settings')
import django
django.setup()



from django.contrib.auth.models import Group,User


all_groups = Group.objects.all()

filename = None
if len(sys.argv) >= 2:
	filename = sys.argv[1]
	f = open(filename,"w")


for g in all_groups:
	#print(g.permissions.all())
	g.name
	permissions = g.permissions.all()
	list_of_codename = [p.codename for p in  permissions]
	to_print = g.name + "|" + ','.join(list_of_codename)
	if filename == None:
		print(to_print)
	else:
		f.write(to_print+"\n")

if filename != None:
	f.close()