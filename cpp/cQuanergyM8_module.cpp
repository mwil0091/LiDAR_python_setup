#ifdef _WIN32
#include <winsock2.h>  // Windows networking headers
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")  // Auto-link Winsock2
#else
#include <arpa/inet.h>  // Unix networking headers
#endif

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <math.h>

#include "LOOKUP_COSINE.h"
#include "LOOKUP_SINE.h"
#include "Quanergy_Packet_Structures.h"

// Use 'float' literals to avoid truncation warnings
const double M8_VERTICAL_ANGLES[] = {
    -0.318505f,
    -0.2692f,
    -0.218009f,
    -0.165195f,
    -0.111003f,
    -0.0557982f,
    0.0f,
    0.0557982f
};

// Explicitly cast to float to avoid C4305 warnings
const float M8_vert_sin[] = {
    static_cast<float>(sin(M8_VERTICAL_ANGLES[0])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[1])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[2])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[3])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[4])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[5])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[6])),
    static_cast<float>(sin(M8_VERTICAL_ANGLES[7]))
};

const float M8_vert_cos[] = {
    static_cast<float>(cos(M8_VERTICAL_ANGLES[0])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[1])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[2])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[3])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[4])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[5])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[6])),
    static_cast<float>(cos(M8_VERTICAL_ANGLES[7]))
};

static PyObject *QuanergyM8_Error;

PyObject* parse_firing_data(PyObject *self, PyObject *args) {
    const char* buffer;
    Py_ssize_t buffer_len;  // Use Py_ssize_t instead of int
    PyArrayObject *pointcloud, *intensities;
    uint32_t start_idx;

    if (!PyArg_ParseTuple(args, "y#OOI", &buffer, &buffer_len, &pointcloud, &intensities, &start_idx)) {
        return NULL;
    }
    	if (buffer_len != 132) {
		PyErr_SetString(QuanergyM8_Error, "buffer must be 132 bytes");
		return NULL;
	}

	if (!PyArray_Check(pointcloud)) {
		PyErr_SetString(QuanergyM8_Error, "pointcloud must be: np.array((N, 3), np.float32)");
		return NULL;
	}

	if (PyArray_NDIM(pointcloud) != 2) {
		PyErr_SetString(QuanergyM8_Error, "pointcloud must be: np.array((N, 3), np.float32)");
		return NULL;
	}
	npy_intp *pcShape = PyArray_SHAPE(pointcloud);
	if (pcShape[1] != 3) {
		PyErr_SetString(QuanergyM8_Error, "pointcloud must be: np.array((N, 3), np.float32)");
		return NULL;
	}

	uint32_t max_offset = start_idx * 3 + 132 * 3;
	if (max_offset >= pcShape[0]) {
		PyErr_Format(PyExc_IndexError,
			"pointcloud array is too small: have %ld rows, but need at least %u rows",
			pcShape[0], max_offset);
		return NULL;
	}

	PyArray_Descr *dtype = PyArray_DTYPE(pointcloud);
	if (dtype->type != 'f') {
		PyErr_SetString(QuanergyM8_Error, "pointcloud must be: np.array((N, 3), np.float32)");
		return NULL;
	}

	if (!PyArray_Check(intensities)) {
		PyErr_SetString(QuanergyM8_Error, "intensities must be an Nx1 array, uint8");
		return NULL;
	}

	float *pcPtr = (float *)PyArray_DATA(pointcloud);
	uint8_t *intenPtr = (uint8_t *)PyArray_DATA(intensities);

	struct M8FiringData *n_firing_data = (struct M8FiringData *) buffer;
	uint16_t angle_10400 = ntohs(n_firing_data->position);
	float rotCos = M8_rot_cosine[angle_10400];
	float rotSin = M8_rot_sine[angle_10400];

	int count = 0;
	int offset = start_idx * 3;
	int returnNum = 0;
	for (int laserNum = 0; laserNum<M8_NUM_LASERS; laserNum++) {
		float vCos = M8_vert_cos[laserNum];
		float vSin = M8_vert_sin[laserNum];

		uint32_t dist = ntohl(n_firing_data->returns_distances[returnNum][laserNum]);
		if (dist > 0) {
			float real_distance = dist * 1e-5;
			pcPtr[offset    ] = real_distance * vCos * rotCos;  // x, in meters
			pcPtr[offset + 1] = real_distance * vCos * rotSin;  // y, in meters
			pcPtr[offset + 2] = real_distance * vSin;           // z, in meters
			intenPtr[offset] = n_firing_data->returns_intensities[returnNum][laserNum];
			offset += 3;
			count++;
		}
	}

	return PyLong_FromLong(count);
}


static PyMethodDef QuanergyM8Methods[] = {
    {"parse_firing_data", parse_firing_data, METH_VARARGS, "Parse Quanergy M8 firing data"},
    {NULL, NULL, 0, NULL}  // Sentinel
};

static struct PyModuleDef cQuanergyM8_module = {
    PyModuleDef_HEAD_INIT,
    "cQuanergyM8",  // Module name (must match Extension name in setup.py)
    NULL,  // Module documentation
    -1,    // Size of per-interpreter module state
    QuanergyM8Methods  // Method table
};

// Module initialization function (MUST match the module name in setup.py)
PyMODINIT_FUNC PyInit_cQuanergyM8(void) {
    import_array();  // Required for NumPy
    return PyModule_Create(&cQuanergyM8_module);
}