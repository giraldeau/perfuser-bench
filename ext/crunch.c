#include <Python.h>
#include <bytearrayobject.h>

PyObject*
do_stride(PyObject* self, PyObject* args)
{
    (void) self, (void) args;
    PyByteArrayObject *src_obj, *dst_obj;
    char *src, *dst;
    Py_ssize_t src_size, dst_size;
    int stride, height, i, j, x, y;

    if (!PyArg_ParseTuple(args, "YYi", &dst_obj, &src_obj, &stride)) {
        Py_RETURN_NONE;
    }

    src = PyByteArray_AS_STRING(src_obj);
    dst = PyByteArray_AS_STRING(dst_obj);
    src_size = PyByteArray_Size((PyObject *)src_obj);
    dst_size = PyByteArray_Size((PyObject *)dst_obj);
    height = src_size / stride;

    for (i = 0; i < stride; i++) {
        for (j = 0; j < height; j++) {
            x = (i * height + j) % dst_size;
            y = (i + j * stride) % src_size;
            dst[x] = src[y];
        }
    }
    Py_RETURN_NONE;
}

static PyMethodDef ProfileBenchMethods[] =
{
    {"stride",       do_stride,     METH_VARARGS, NULL},
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
