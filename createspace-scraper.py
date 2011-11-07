import re
import sys
import requests
from BeautifulSoup import BeautifulSoup

def get_sales(email, password, date_start, date_end):
	"""
	Returns the number of item sales and the total revenue between
	the two dates passed (inclusive) as a tuple

	Dates should be in the format YEAR-MONTH-DAY (e.g. 2011-11-30)
	"""

	session = requests.session()

	# Login
	r = session.post('https://www.createspace.com/LoginProc.do', data = {
		'redirectURL': '',
		'reason': '',
		'Log In': 'action',
		'login': email,
		'password': password
	})

	# Initialise report (need a valid report ID)
	r = session.get('https://www.createspace.com/pub/reports/init.salesdetails.do?msk=mr')

	# Looking for the value attribute:
	# <input type="hidden" name="value(member.reports.displaysearchid:4)" value="QA5j9Isd" id="member_reports_displaysearchid:4">
	match = re.search('member\.reports\.displaysearchid:5\)" value="(\w*)"', r.content)

	if not match:
		raise Exception('Could not extract token')
		exit()

	token = match.group(1)

	# Kick-off the report server-side
	r = session.post('https://www.createspace.com/pub/reports/ajax/search.salesdetails.do', {
		'value(member.reports.dateoptions)': 'CUSTOM',
		'value(member.reports.startdate)': date_start,
		'value(member.reports.enddate)': date_end,
		'value(member.reports.identifieroptions)': 'OTHER',
		'value(member.reports.identifier)': '',
		'value(member.reports.saleschannelsall)': 'SHOW_ALL',
		'value(member.reports.producttypesall)': 'SHOW_ALL',
		'value(member.reports.paymentstatusfilter)': 'SHOW_ALL',
		'value(member.reports.paymentnumber)': '',
		'value(member.reports.displaysearchid:5)': token
	})

	# Fetch the generated report details
	r = session.post('https://www.createspace.com/pub/reports/ajax/table.salesdetails.do?sid=' + token + '&msk=mr')

	markup = BeautifulSoup(r.content)
	markupHeadingBlock = markup.find('tr', {'class': 'head2'})
	totalQuantity = markupHeadingBlock.find(text = re.compile('\d+'))
	totalValue = markupHeadingBlock.find(text = re.compile('\$\d+'))

	# Cleanup the data
	if totalQuantity is None:
		totalQuantity = 0
	else:
		totalQuantity = int(totalQuantity.strip())
	
	if totalValue is None:
		totalValue = float(0)
	else:
		totalValue = float(totalValue.strip().replace('$', ''))

	return (totalQuantity, totalValue)

def main():

	if len(sys.argv) != 5:
		print 'Missing arguments'
		exit()

	email = sys.argv[1]
	password = sys.argv[2]
	date_start = sys.argv[3]
	date_end = sys.argv[4]

	data = get_sales(email, password, date_start, date_end)
	print str(data[0]) + ' ' + str(data[1])

if __name__ == '__main__':
	main()