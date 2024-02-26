from django.contrib import admin

from .models import Category, Comments, Location, Post


class PostInline(admin.TabularInline):
    """Добавление информации о постах в информации о категории"""

    model = Post
    extra = 0


class PostAdmin(admin.ModelAdmin):
    """Настройка вывода информации о постах"""

    list_display = (
        'id',
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'location',
        'text'
    )
    search_fields = ('title',)
    list_filter = ('category', 'author', 'location', 'category')
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    """Настройка вывода информации о категориях"""

    inlines = (
        PostInline,
    )
    list_display = (
        'id',
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    list_filter = ('is_published',)
    list_display_links = ('title',)


class LocationAdmin(admin.ModelAdmin):
    """Настройка вывода информации о локации"""

    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    list_filter = ('is_published',)
    list_display_links = ('name',)


class CommentsAdmin(admin.ModelAdmin):
    """Настройка вывода информации о комментариях"""

    list_display = (
        'id',
        'text',
        'created_at',
        'post',
        'author',
    )
    list_display_links = ('id',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comments, CommentsAdmin)
