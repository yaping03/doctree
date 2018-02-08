from django import template
# from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='page')
def page(request, p):
	get = request.GET.copy()
	get['page'] = p

	return "?"+get.urlencode()

@register.filter(name='is_selected')
def is_selected(from_id, to_id):
	result = ""	
	if from_id == str(to_id):
		result = "selected"
	return result

@register.filter(name="get_field")
def get_field(request, field):
	return request.GET.get(field)

@register.filter(name="near_range")
def near_range(pagination):
	half_range = 3
	current = pagination.number
	start = current-half_range
	if start<1:
		start = 1
	end = current+half_range
	if end>pagination.paginator.num_pages:
		end = pagination.paginator.num_pages

	return range(start, end+1)

@register.filter(name="none_2_null")
def none_2_null(str):
	result = str
	if (not str) or str.lower()=="none":
		result = ""
	return result

@register.filter(name="enum")
def enum(arr):

	return enumerate(arr)