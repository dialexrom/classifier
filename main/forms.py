from django import forms


class addForm(forms.Form):
    path_to_file = forms.FileField(label="Storing file", required=True)


class textForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 160}),
        label="Text"
    )


class filterForm(forms.Form):
    selected_label = forms.ChoiceField(
        choices=(("All", "All"), ("MAGAZINE", "MAGAZINE"), ("ANIMALS", "ANIMALS")),
        label="Filter",
        required=False,
        initial="All",
    )
    sorting = forms.ChoiceField(
        choices=((0, "The oldest first"), (1, "The newest first")),
        initial=0,
        label="Sort",
    )
