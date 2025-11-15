from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hall


@login_required
def hall_list(request):
    if not request.user.is_admin:
        return redirect("home")  # or raise 403

    halls = Hall.objects.filter(admin=request.user)
    return render(request, "halls/hall_list.html", {"halls": halls})


@login_required
def hall_form_view(request, pk=None):
    if not request.user.is_admin:
        return redirect("home")

    hall = None
    if pk:
        hall = get_object_or_404(Hall, pk=pk, admin=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        layout_json = request.POST.get("layout")  # JSON string from JS designer
        capacity = request.POST.get("capacity", 0)

        if hall:
            hall.name = name
            hall.layout = layout_json
            hall.capacity = capacity
            hall.save()
        else:
            hall = Hall.objects.create(
                admin=request.user,
                name=name,
                layout=layout_json,
                capacity=capacity
            )

        return redirect("hall_list")

    # Default grid size (12x12)
    rows = 12
    cols = 12

    return render(
        request,
        "halls/hall_form.html",
        {"hall": hall, "rows": range(rows), "cols": range(cols)}
    )


@login_required
def hall_delete(request, pk):
    hall = get_object_or_404(Hall, pk=pk, admin=request.user)

    if request.method == "POST":
        hall.delete()
        return redirect("hall_list")

    return render(request, "halls/hall_confirm_delete.html", {"hall": hall})
