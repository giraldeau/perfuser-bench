#include <Python.h>
#include <bytearrayobject.h>

PyObject*
do_crunch(PyObject* self, PyObject* args)
{
    (void) self, (void) args;
    printf("do_crunch %p %p\n", self, args);
    Py_RETURN_NONE;
}

static PyMethodDef ProfileBenchMethods[] =
{
    {"crunch",       do_crunch,     METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "ext",
        NULL,
        0,
        ProfileBenchMethods,
        NULL,
        NULL,
        NULL,
        NULL
};

PyMODINIT_FUNC
PyInit_ext(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    return module;
}
