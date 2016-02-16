from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import loader
from .models import Question


# Create your views here.
#def index(request):
#    return HttpResponse("Hello, JUANMA. You're at the juanmaapp index.")

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('juanmaapp/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))

def upload(request):
#    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('juanmaapp/uploadform.html')
#    context = {
 #       'latest_question_list': latest_question_list,
 #   }
    return render(request, 'juanmaapp/uploadform.html')

 
#def index(request):
#    latest_question_list = Question.objects.order_by('-pub_date')[:5]
#    output = ', '.join([q.question_text for q in latest_question_list])
#    return HttpResponse(output)


#def detail(request, question_id):
#    return HttpResponse("You're looking at question %s." % question_id)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'juanmaapp/detail.html', {'question': question})
#def results(request, question_id):
#    response = "You're looking at the results of question %s."
#    return HttpResponse(response % question_id)

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'juanmaapp/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'juanmaapp/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('juanmaapp:results', args=(question.id,)))

