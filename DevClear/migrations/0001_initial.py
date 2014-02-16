# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organization'
        db.create_table(u'DevClear_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'DevClear', ['Organization'])

        # Adding M2M table for field members on 'Organization'
        m2m_table_name = db.shorten_name(u'DevClear_organization_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm[u'DevClear.organization'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organization_id', 'user_id'])

        # Adding M2M table for field projects on 'Organization'
        m2m_table_name = db.shorten_name(u'DevClear_organization_projects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm[u'DevClear.organization'], null=False)),
            ('project', models.ForeignKey(orm[u'DevClear.project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organization_id', 'project_id'])

        # Adding model 'Organization_Perms'
        db.create_table(u'DevClear_organization_perms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Organization_uperms', null=True, to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Organization_gperms', null=True, to=orm['auth.Group'])),
            ('obj', self.gf('django.db.models.fields.related.ForeignKey')(related_name='operms', to=orm['DevClear.Organization'])),
            ('edit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('add_project', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('add_member', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('remove', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('view', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('DevClear', ['Organization_Perms'])

        # Adding model 'Project'
        db.create_table(u'DevClear_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sponsor_org', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['DevClear.Organization'])),
            ('scale', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=2)),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'DevClear', ['Project'])

        # Adding M2M table for field members on 'Project'
        m2m_table_name = db.shorten_name(u'DevClear_project_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'DevClear.project'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table(u'DevClear_organization')

        # Removing M2M table for field members on 'Organization'
        db.delete_table(db.shorten_name(u'DevClear_organization_members'))

        # Removing M2M table for field projects on 'Organization'
        db.delete_table(db.shorten_name(u'DevClear_organization_projects'))

        # Deleting model 'Organization_Perms'
        db.delete_table(u'DevClear_organization_perms')

        # Deleting model 'Project'
        db.delete_table(u'DevClear_project')

        # Removing M2M table for field members on 'Project'
        db.delete_table(db.shorten_name(u'DevClear_project_members'))


    models = {
        u'DevClear.organization': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Organization'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['DevClear.Project']", 'symmetrical': 'False', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'DevClear.organization_perms': {
            'Meta': {'object_name': 'Organization_Perms'},
            'add_member': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'add_project': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'edit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Organization_gperms'", 'null': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'operms'", 'to': u"orm['DevClear.Organization']"}),
            'remove': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Organization_uperms'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'view': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'DevClear.project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scale': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'sponsor_org': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['DevClear.Organization']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '2'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['DevClear']