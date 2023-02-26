from django.shortcuts import render, redirect


def create_form(request):
    if request.method == 'POST':
        print("////////////////////////////////////")
        print(request.POST['code'])
        print("////////////////////////////////////")

    return render(request, 'create_form.html', {})
