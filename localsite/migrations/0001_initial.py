# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Hall'
        db.create_table('localsite_hall', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('localsite', ['Hall'])

        # Adding model 'HallScheme'
        db.create_table('localsite_hallscheme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('hall', self.gf('django.db.models.fields.related.ForeignKey')(related_name='schemes', to=orm['localsite.Hall'])),
            ('substrate', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('localsite', ['HallScheme'])

        # Adding model 'EventCategory'
        db.create_table('localsite_eventcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=25, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['localsite.EventCategory'])),
        ))
        db.send_create_signal('localsite', ['EventCategory'])

        # Adding model 'Event'
        db.create_table('localsite_event', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('hallscheme', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['localsite.HallScheme'])),
        ))
        db.send_create_signal('localsite', ['Event'])

        # Adding model 'EventDate'
        db.create_table('localsite_eventdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dates', to=orm['localsite.Event'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('localsite', ['EventDate'])

        # Adding model 'SeatLocation'
        db.create_table('localsite_seatlocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hallscheme', self.gf('django.db.models.fields.related.ForeignKey')(related_name='seats', to=orm['localsite.HallScheme'])),
            ('sec', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('row', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('col', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('x_position', self.gf('django.db.models.fields.IntegerField')()),
            ('y_position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('localsite', ['SeatLocation'])

        # Adding model 'Ticket'
        db.create_table('localsite_ticket', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('localsite', ['Ticket'])


    def backwards(self, orm):
        
        # Deleting model 'Hall'
        db.delete_table('localsite_hall')

        # Deleting model 'HallScheme'
        db.delete_table('localsite_hallscheme')

        # Deleting model 'EventCategory'
        db.delete_table('localsite_eventcategory')

        # Deleting model 'Event'
        db.delete_table('localsite_event')

        # Deleting model 'EventDate'
        db.delete_table('localsite_eventdate')

        # Deleting model 'SeatLocation'
        db.delete_table('localsite_seatlocation')

        # Deleting model 'Ticket'
        db.delete_table('localsite_ticket')


    models = {
        'localsite.event': {
            'Meta': {'object_name': 'Event'},
            'hallscheme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['localsite.HallScheme']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'localsite.eventcategory': {
            'Meta': {'object_name': 'EventCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['localsite.EventCategory']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'})
        },
        'localsite.eventdate': {
            'Meta': {'object_name': 'EventDate'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': "orm['localsite.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'localsite.hall': {
            'Meta': {'object_name': 'Hall'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'localsite.hallscheme': {
            'Meta': {'object_name': 'HallScheme'},
            'hall': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schemes'", 'to': "orm['localsite.Hall']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'substrate': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'localsite.seatlocation': {
            'Meta': {'object_name': 'SeatLocation'},
            'col': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hallscheme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'seats'", 'to': "orm['localsite.HallScheme']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sec': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'x_position': ('django.db.models.fields.IntegerField', [], {}),
            'y_position': ('django.db.models.fields.IntegerField', [], {})
        },
        'localsite.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.category': {
            'Meta': {'ordering': "['site', 'parent__id', 'ordering', 'name']", 'unique_together': "(('site', 'slug'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_categories_rel_+'", 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.product': {
            'Meta': {'ordering': "('site', 'ordering', 'name')", 'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'also_purchased_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'height_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'length_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_items_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'DEFAULT'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'total_sold': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['localsite']
