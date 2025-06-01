/*
 * B+ Tree Python Extension Module
 * 
 * Python C API implementation for high-performance B+ tree.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"
#include "bplustree.h"
/* GC clear/traverse prototypes */
static int BPlusTree_traverse(BPlusTree *self, visitproc visit, void *arg);
static int BPlusTree_clear(BPlusTree *self);

/* Method implementations */

PyObject *
BPlusTree_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    BPlusTree *self = PyObject_GC_New(BPlusTree, type);
    if (self != NULL) {
        self->root = NULL;
        self->leaves = NULL;
        self->capacity = DEFAULT_CAPACITY;
        self->min_keys = DEFAULT_CAPACITY / 2;
        self->size = 0;
        PyObject_GC_Track(self);
    }
    return (PyObject *)self;
}

int
BPlusTree_init(BPlusTree *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"capacity", NULL};
    int capacity = DEFAULT_CAPACITY;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &capacity)) {
        return -1;
    }
    
    if (capacity < MIN_CAPACITY) {
        PyErr_Format(PyExc_ValueError, 
                     "capacity must be at least %d, got %d", 
                     MIN_CAPACITY, capacity);
        return -1;
    }
    
    self->capacity = capacity;
    self->min_keys = capacity / 2;
    
    /* Create initial root (leaf) */
    self->root = node_create(NODE_LEAF, capacity);
    if (!self->root) {
        return -1;
    }
    self->leaves = self->root;
    
    
    return 0;
}

void
BPlusTree_dealloc(BPlusTree *self) {
    PyObject_GC_UnTrack(self);
    BPlusTree_clear(self);
    if (self->root) {
        node_destroy(self->root);
    }
    PyObject_GC_Del(self);
}

PyObject *
BPlusTree_getitem(BPlusTree *self, PyObject *key) {
    return tree_get(self, key);
}

int
BPlusTree_setitem(BPlusTree *self, PyObject *key, PyObject *value) {
    if (value == NULL) {
        return BPlusTree_delitem(self, key);
    }
    return tree_insert(self, key, value);
}

int
BPlusTree_delitem(BPlusTree *self, PyObject *key) {
    int result = tree_delete(self, key);
    if (result == -1) return -1;  /* Error already set */
    if (result == 0) {
        /* Key not found */
        PyErr_SetObject(PyExc_KeyError, key);
        return -1;
    }
    return 0;  /* Success */
}

Py_ssize_t
BPlusTree_length(BPlusTree *self) {
    return self->size;
}

int
BPlusTree_contains(BPlusTree *self, PyObject *key) {
    PyObject *value = tree_get(self, key);
    if (value) {
        Py_DECREF(value);
        return 1;
    }
    PyErr_Clear();
    return 0;
}

/* Iterator implementation */

typedef struct {
    PyObject_HEAD
    BPlusTree *tree;
    BPlusNode *current_node;
    int current_index;
    int include_values;  /* 0 for keys(), 1 for items() */
} BPlusTreeIterator;

static void
BPlusTreeIterator_dealloc(BPlusTreeIterator *self) {
    Py_XDECREF(self->tree);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
BPlusTreeIterator_next(BPlusTreeIterator *self) {
    if (!self->current_node) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    
    if (self->current_index >= self->current_node->num_keys) {
        self->current_node = self->current_node->next;
        self->current_index = 0;
        
        if (!self->current_node) {
            PyErr_SetNone(PyExc_StopIteration);
            return NULL;
        }
    }
    
    PyObject *key = node_get_key(self->current_node, self->current_index);
    
    if (self->include_values) {
        PyObject *value = node_get_value(self->current_node, self->current_index);
        PyObject *tuple = PyTuple_New(2);
        if (!tuple) return NULL;
        
        Py_INCREF(key);
        Py_INCREF(value);
        PyTuple_SET_ITEM(tuple, 0, key);
        PyTuple_SET_ITEM(tuple, 1, value);
        self->current_index++;
        return tuple;
    } else {
        self->current_index++;
        Py_INCREF(key);
        return key;
    }
}

static PyTypeObject BPlusTreeIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "bplustree_c.BPlusTreeIterator",
    .tp_basicsize = sizeof(BPlusTreeIterator),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)BPlusTreeIterator_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "B+ tree iterator",
    .tp_iter = PyObject_SelfIter,
    .tp_iternext = (iternextfunc)BPlusTreeIterator_next,
};

static PyObject *
BPlusTree_iter(BPlusTree *self) {
    BPlusTreeIterator *iter = PyObject_New(BPlusTreeIterator, &BPlusTreeIteratorType);
    if (!iter) return NULL;
    
    Py_INCREF(self);
    iter->tree = self;
    iter->current_node = self->leaves;
    iter->current_index = 0;
    iter->include_values = 0;
    
    return (PyObject *)iter;
}

static PyObject *
BPlusTree_keys(BPlusTree *self, PyObject *Py_UNUSED(ignored)) {
    return BPlusTree_iter(self);
}

static PyObject *
BPlusTree_items(BPlusTree *self, PyObject *Py_UNUSED(args)) {
    BPlusTreeIterator *iter = PyObject_New(BPlusTreeIterator, &BPlusTreeIteratorType);
    if (!iter) return NULL;
    
    Py_INCREF(self);
    iter->tree = self;
    iter->current_node = self->leaves;
    iter->current_index = 0;
    iter->include_values = 1;
    
    return (PyObject *)iter;
}


/* Method definitions */

static PyMethodDef BPlusTree_methods[] = {
    {"keys", (PyCFunction)BPlusTree_keys, METH_NOARGS,
     "Return an iterator over the tree's keys"},
    {"items", (PyCFunction)BPlusTree_items, METH_VARARGS,
     "Return an iterator over the tree's (key, value) pairs"},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

/* Mapping protocol */

static PyMappingMethods BPlusTree_as_mapping = {
    (lenfunc)BPlusTree_length,
    (binaryfunc)BPlusTree_getitem,
    (objobjargproc)BPlusTree_setitem
};

/* Module-level methods for testing and diagnostics */
static PyObject *
py_check_data_alignment(PyObject *self, PyObject *args)
{
    unsigned int capacity = DEFAULT_CAPACITY;
    if (!PyArg_ParseTuple(args, "|I", &capacity)) {
        return NULL;
    }
    BPlusNode *node = node_create(NODE_LEAF, capacity);
    if (!node) {
        return NULL;
    }
    uintptr_t addr = (uintptr_t)node->data;
    node_destroy(node);
    if (addr % CACHE_LINE_SIZE == 0) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PyMethodDef module_methods[] = {
    {"_check_data_alignment", py_check_data_alignment, METH_VARARGS,
     "Return True if node->data is aligned to CACHE_LINE_SIZE (optional capacity)"},
    {NULL, NULL, 0, NULL}
};

/* Sequence protocol (for 'in' operator) */

static PySequenceMethods BPlusTree_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    (objobjproc)BPlusTree_contains, /* sq_contains */
};

/* Common GC operation: traverse or clear Python references in a node and its children. */
static int
node_gc_op(BPlusNode *node, visitproc visit, void *arg, int clear)
{
    if (!node) {
        return 0;
    }
    for (int i = 0; i < node->num_keys; i++) {
        if (clear) {
            Py_CLEAR(node->data[i]);
        } else {
            Py_VISIT(node_get_key(node, i));
        }
    }
    if (node->type == NODE_LEAF) {
        for (int i = 0; i < node->num_keys; i++) {
            if (clear) {
                Py_CLEAR(node->data[node->capacity + i]);
            } else {
                Py_VISIT(node_get_value(node, i));
            }
        }
    } else {
        for (int i = 0; i <= node->num_keys; i++) {
            BPlusNode *child = node_get_child(node, i);
            if (clear) {
                node_gc_op(child, NULL, NULL, 1);
            } else if (child && node_gc_op(child, visit, arg, 0)) {
                return -1;
            }
        }
    }
    return 0;
}

static int
node_traverse(BPlusNode *node, visitproc visit, void *arg)
{
    return node_gc_op(node, visit, arg, 0);
}


static int
BPlusTree_traverse(BPlusTree *self, visitproc visit, void *arg) {
    if (self->root) {
        if (node_traverse(self->root, visit, arg) != 0) {
            return -1;
        }
    }
    return 0;
}


static int
BPlusTree_clear(BPlusTree *self) {
    if (self->root) {
        node_clear_gc(self->root);
    }
    return 0;
}

/* Type definition */

static PyTypeObject BPlusTreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "bplustree_c.BPlusTree",
    .tp_doc = "High-performance B+ tree implementation",
    .tp_basicsize = sizeof(BPlusTree),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = BPlusTree_new,
    .tp_init = (initproc)BPlusTree_init,
    .tp_dealloc = (destructor)BPlusTree_dealloc,
    .tp_traverse = (traverseproc)BPlusTree_traverse,
    .tp_clear = (inquiry)BPlusTree_clear,
    .tp_as_mapping = &BPlusTree_as_mapping,
    .tp_as_sequence = &BPlusTree_as_sequence,
    .tp_methods = BPlusTree_methods,
    .tp_iter = (getiterfunc)BPlusTree_iter,
};

/* Module definition */

static PyModuleDef bplustree_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "bplustree_c",
    .m_doc = "High-performance B+ tree C extension",
    .m_size = -1,
    .m_methods = module_methods,
};

PyMODINIT_FUNC
PyInit_bplustree_c(void) {
    PyObject *m;
    
    if (PyType_Ready(&BPlusTreeType) < 0)
        return NULL;
    
    if (PyType_Ready(&BPlusTreeIteratorType) < 0)
        return NULL;
    
    m = PyModule_Create(&bplustree_module);
    if (m == NULL)
        return NULL;
    
    Py_INCREF(&BPlusTreeType);
    if (PyModule_AddObject(m, "BPlusTree", (PyObject *)&BPlusTreeType) < 0) {
        Py_DECREF(&BPlusTreeType);
        Py_DECREF(m);
        return NULL;
    }
    
    return m;
}