from django.contrib import admin

from .models import Article, ArticleLike, Comment, CommentVote


class CommentInlineAdmin(admin.StackedInline):
    model = Comment

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ('likes_amount', 'special_likes_amount', 'comments_amount')
    inlines = [CommentInlineAdmin]


class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('score',)


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleLike)

admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentVote)
