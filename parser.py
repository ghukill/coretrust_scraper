from bs4 import BeautifulSoup
import os
import requests
import re
import pickle

# parse
with open('all.html','r') as f:
	html_doc = f.read()
soup = BeautifulSoup(html_doc)


# get all repos
trs = soup.find_all('tr')
repos = trs[1:-6]


# loop through
repo_ds = []
for repo in repos:

	#
	repo_d = {}

	# find icon type
	icon_hash = {
		'https://www.coretrustseal.org/wp-content/uploads/leaflet-maps-marker-icons/CTS.png':'c',
		'https://www.coretrustseal.org/wp-content/uploads/leaflet-maps-marker-icons/DSA.png':'d',
		'https://www.coretrustseal.org/wp-content/uploads/leaflet-maps-marker-icons/WDS.png':'w',
		'https://www.coretrustseal.org/wp-content/uploads/leaflet-maps-marker-icons/WDSA-3.png':'dw'
	}
	icon_p = repo.find('td',{'class':'lmm-listmarkers-icon'})
	img = next(icon_p.children)
	repo_type = icon_hash[img.attrs['src']]
	print(repo_type)
	repo_d['type'] = repo_type

	# grab name
	name = repo.find('span',{'class':'lmm-listmarkers-markername'}).text
	print(name)
	repo_d['name'] = name

	# address (if exists)
	try:
		address = repo.find('div',{'class':'lmm-listmarkers-hr'}).text
	except:
		address = None
	print(address)
	repo_d['address'] = address

	# HANDLE TYPES

	# c
	if repo_type == 'c':

		# get p
		p = repo.find('p')

		# get first link
		repo_d['homepage'] = p.find('a').text

		# download pdf
		for a in p.find_all('a'):
			if a.text == 'CoreTrustSeal certification 2017-2019':
				cert_pdf_url = a.attrs['href']
				repo_d['cert_pdf_url'] = cert_pdf_url
				filename = cert_pdf_url.split('/')[-1]
				if not os.path.exists('c/%s' % filename):
					r = requests.get(cert_pdf_url)
					with open('c/%s' % filename, 'wb') as f:
						f.write(r.content)

	# d
	if repo_type == 'd':

		# get p
		p = repo.find('p')

		# get first link
		repo_d['homepage'] = p.find('a').text

		# get dsa date
		date = re.match(r'.*DSA seal date: (.+?)DSA Seal', p.text).groups()[0]
		repo_d['cert_date'] = date

		# download pdf
		for a in p.find_all('a'):
			if a.text == 'DSA Seal':
				data_seal_pdf = a.attrs['href']
				repo_d['data_seal_pdf'] = data_seal_pdf
				filename = '%s.pdf' % name.replace(' ','_').replace('/','-')
				if not os.path.exists('d/%s' % filename):
					r = requests.get(data_seal_pdf)
					with open('d/%s' % filename, 'wb') as f:
						f.write(r.content)


	# w
	if repo_type == 'w':

		# get p
		p = repo.find('p')

		# get first link
		repo_d['homepage'] = p.find('a').text

		# get dsa date
		try:
			date = re.match(r'.*WDS Regular Member certification date: (.+?)WDS Regular Members', p.text).groups()[0]
			repo_d['cert_date'] = date
		except:
			repo_d['cert_date'] = None

	# dw
	if repo_type == 'dw':
		pass


	# append
	repo_ds.append(repo_d)


# pickle
pickle.dump(repo_ds,open('repos.pickle','wb'))

# write to csvs