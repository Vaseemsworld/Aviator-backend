from django.contrib import admin
from .models import CustomUser, WalletTransaction, OTP
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.shortcuts import redirect, render

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ("phone", "username", "balance", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("phone", "username")
    ordering = ("phone",)

    fieldsets = (
        (None, {"fields": ("phone", "username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Wallet Info", {"fields": ("balance",)}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "username", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

class RejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.CharField(widget=forms.Textarea, label="Rejection Reason", required=True)

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount", "timestamp")
    list_filter = ("type", "timestamp")
    search_fields = ("user__phone",)
    readonly_fields = ("timestamp",)
    
    actions = ["approve_transactions", "reject_transactions"]

    @admin.action(description="Approve selected transactions")
    def approve_transactions(self, request, queryset):
        for transaction in queryset.filter(status='pending'):
            user = transaction.user
            print('debug: ', transaction.type)

            if transaction.type.upper() == 'DEPOSIT':
                user.balance += transaction.amount
                user.save()

            elif transaction.type.upper() == 'WITHDRAW':
                print(f'balance: {user.balance} found withdraw for user {user.phone} with amount {transaction.amount}')
                if user.balance >= transaction.amount:
                    user.balance -= transaction.amount
                    user.save()
                else:
                    self.message_user(
                        request,
                        f"Insufficient balance",
                        level='error'
                    )
                    continue
            
            transaction.status = 'success'
            transaction.save()

    @admin.action(description="Reject with reason")
    def reject_transactions_with_reason(self, request, queryset):
        if 'apply' in request.POST:
            form = RejectForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                for txn in queryset.filter(status='pending'):
                    txn.status = 'rejected'
                    txn.rejection_reason = reason
                    txn.save()
                self.message_user(request, "Selected transactions rejected with reason.")
                return redirect(request.get_full_path())
        else:
            form = RejectForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render(request, 'admin/reject_reason.html', {
            'transactions': queryset,
            'form': form,
            'title': 'Reject transactions with reason'
        })
    
    @admin.action(description="Reject selected transactions")
    def reject_transactions(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')



# @admin.register(OTP)
# class OTPAdmin(admin.ModelAdmin):
#     list_display = ("phone", "code", "created_at")
#     search_fields = ("phone",)
#     readonly_fields = ("code", "created_at")

#     def has_add_permission(self, request):
#         return False  # Disable manual add

#     def has_change_permission(self, request, obj=None):
#         return False  # Disable edit
