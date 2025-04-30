from django.contrib import admin
from .models import Post, Multimedia, Comentario, Like


class MultimediaInline(admin.TabularInline):
    model = Multimedia
    extra = 1


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'contenido', 'fecha_creacion')
    can_delete = False
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_creacion', 'es_publico', 'total_likes', 'total_comentarios')
    list_filter = ('es_publico', 'fecha_creacion')
    search_fields = ('usuario__username', 'contenido')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    inlines = [MultimediaInline, ComentarioInline]


@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'tipo', 'titulo', 'fecha_subida')
    list_filter = ('tipo', 'fecha_subida')
    search_fields = ('titulo', 'descripcion', 'post__usuario__username')
    date_hierarchy = 'fecha_subida'


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'usuario', 'fecha_creacion', 'comentario_padre')
    list_filter = ('fecha_creacion',)
    search_fields = ('usuario__username', 'contenido', 'post__contenido')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'usuario', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('usuario__username', 'post__contenido')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)
