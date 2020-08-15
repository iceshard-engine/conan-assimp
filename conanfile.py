from conans import ConanFile, CMake, tools
import os


class AssimpConan(ConanFile):
    name = "Assimp"
    version = "5.0.1"
    license = "BSD 3-Clause"
    homepage = "https://github.com/assimp/assimp"
    url = "https://github.com/jacmoe/conan-assimp"
    description = "Conan package for Assmip"
    requires = "zlib/1.2.11@conan/stable"
    settings = "os", "compiler", "arch"

    _source_subfolder = "sources"
    _build_subfolder = "build"

    options = {
        "shared": [True, False],
        "double_precision": [True, False],
        "no_export": [True, False],
        "internal_irrxml": [True, False],
        "fPIC": [True, False],
    }

    # only fPIC enabled by default
    default_options = ("=False\n".join(options.keys()) + "=False\n").replace("fPIC=False", "fPIC=True").replace("internal_irrxml=False", "internal_irrxml=True")

    # Format available options
    _format_option_map = {
        "with_3d": "ASSIMP_BUILD_3D_IMPORTER",
        "with_3ds": "ASSIMP_BUILD_3DS_IMPORTER",
        "with_3mf": "ASSIMP_BUILD_3MF_IMPORTER",
        "with_ac": "ASSIMP_BUILD_AC_IMPORTER",
        "with_amf": "ASSIMP_BUILD_AMF_IMPORTER",
        "with_ase": "ASSIMP_BUILD_ASE_IMPORTER",
        "with_assbin": "ASSIMP_BUILD_ASSBIN_IMPORTER",
        "with_assxml": "ASSIMP_BUILD_ASSXML_IMPORTER",
        "with_b3d": "ASSIMP_BUILD_B3D_IMPORTER",
        "with_blend": "ASSIMP_BUILD_BLEND_IMPORTER",
        "with_bvh": "ASSIMP_BUILD_BVH_IMPORTER",
        "with_cob": "ASSIMP_BUILD_COB_IMPORTER",
        "with_collada": "ASSIMP_BUILD_COLLADA_IMPORTER",
        "with_csm": "ASSIMP_BUILD_CSM_IMPORTER",
        "with_dxf": "ASSIMP_BUILD_DXF_IMPORTER",
        "with_fbx": "ASSIMP_BUILD_FBX_IMPORTER",
        "with_gltf": "ASSIMP_BUILD_GLTF_IMPORTER",
        "with_hmp": "ASSIMP_BUILD_HMP_IMPORTER",
        "with_ifc": "ASSIMP_BUILD_IFC_IMPORTER",
        "with_irr": "ASSIMP_BUILD_IRR_IMPORTER",
        "with_irrmesh": "ASSIMP_BUILD_IRRMESH_IMPORTER",
        "with_lwo": "ASSIMP_BUILD_LWO_IMPORTER",
        "with_lws": "ASSIMP_BUILD_LWS_IMPORTER",
        "with_md2": "ASSIMP_BUILD_MD2_IMPORTER",
        "with_md3": "ASSIMP_BUILD_MD3_IMPORTER",
        "with_md5": "ASSIMP_BUILD_MD5_IMPORTER",
        "with_mdc": "ASSIMP_BUILD_MDC_IMPORTER",
        "with_mdl": "ASSIMP_BUILD_MDL_IMPORTER",
        "with_mmd": "ASSIMP_BUILD_MMD_IMPORTER",
        "with_ms3d": "ASSIMP_BUILD_MS3D_IMPORTER",
        "with_ndo": "ASSIMP_BUILD_NDO_IMPORTER",
        "with_nff": "ASSIMP_BUILD_NFF_IMPORTER",
        "with_obj": "ASSIMP_BUILD_OBJ_IMPORTER",
        "with_off": "ASSIMP_BUILD_OFF_IMPORTER",
        "with_ogre": "ASSIMP_BUILD_OGRE_IMPORTER",
        "with_opengex": "ASSIMP_BUILD_OPENGEX_IMPORTER",
        "with_ply": "ASSIMP_BUILD_PLY_IMPORTER",
        "with_q3bsp": "ASSIMP_BUILD_Q3BSP_IMPORTER",
        "with_q3d": "ASSIMP_BUILD_Q3D_IMPORTER",
        "with_raw": "ASSIMP_BUILD_RAW_IMPORTER",
        "with_sib": "ASSIMP_BUILD_SIB_IMPORTER",
        "with_smd": "ASSIMP_BUILD_SMD_IMPORTER",
        "with_stl": "ASSIMP_BUILD_STL_IMPORTER",
        "with_terragen": "ASSIMP_BUILD_TERRAGEN_IMPORTER",
        "with_x": "ASSIMP_BUILD_X_IMPORTER",
        "with_x3d": "ASSIMP_BUILD_X3D_IMPORTER",
        "with_xgl": "ASSIMP_BUILD_XGL_IMPORTER",
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))

    # All format options enabled by default
    default_options += "=True\n".join(_format_option_map.keys()) + "=True"

    build_requires = "cmake_installer/3.15.5@conan/stable"
    generators = "cmake"

    exports = ["LICENSE.md"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            del self.settings.compiler.runtime

    def requirements(self):
        if not self.options.internal_irrxml:
            # Using requirement from conan-center
            self.requires.add("IrrXML/1.2@conan/stable")

    def source(self):
        source_url = "{}/archive/v{}.zip".format(self.homepage, self.version)
        tools.get(source_url)
        os.rename("assimp-{}".format(self.version), self._source_subfolder)

        tools.replace_in_file("{}/CMakeLists.txt".format(self._source_subfolder), "PROJECT( Assimp VERSION 5.0.0 )", """PROJECT( Assimp VERSION 5.0.0 )
include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()""")

    def _configure_cmake(self, build_type):
        cmake = CMake(self, build_type=build_type)
        # Use conan-irrxml instead of irrxml included in assimp
        cmake.definitions["SYSTEM_IRRXML"] = not self.options.internal_irrxml

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        cmake.definitions["ASSIMP_NO_EXPORT"] = self.options.no_export
        cmake.definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        cmake.definitions["ASSIMP_BUILD_TESTS"] = False
        cmake.definitions["ASSIMP_BUILD_SAMPLES"] = False
        cmake.definitions["ASSIMP_BUILD_ZLIB"] = True
        cmake.definitions["ASSIMP_INSTALL_PDB"] = False

        # Disabling ASSIMP_ANDROID_JNIIOSYSTEM, failing in cmake install
        cmake.definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False

        if self.settings.os != "Windows":
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        # Enable/Disable format importer options in cmake
        cmake.definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        for option, definition in self._format_option_map.items():
            cmake.definitions[definition] = bool(getattr(self.options, option))

        cmake.configure(source_folder=self._source_subfolder, build_folder="{}_{}".format(self._build_subfolder, build_type))
        return cmake

    def build(self):
        cmake = self._configure_cmake(build_type="Debug")
        cmake.build()
        cmake = self._configure_cmake(build_type="Release")
        cmake.build()

    def package(self):
        # There are more than one LICENSE in source tree, choosing package and src license
        self.copy("LICENSE.md", dst="licenses", keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder, keep_path=False)

        self.copy("*.h", dst="include", src="{}/include".format(self._source_subfolder))
        self.copy("*.hpp", dst="include", src="{}/include".format(self._source_subfolder))
        self.copy("*.inl", dst="include", src="{}/include".format(self._source_subfolder))

        build_artifacts_debug = "{}_{}".format(self._build_subfolder, "Debug")
        build_artifacts_release = "{}_{}".format(self._build_subfolder, "Release")

        self.copy("*.h", dst="include_debug", src="{}/include".format(build_artifacts_debug))
        self.copy("*.h", dst="include_release", src="{}/include".format(build_artifacts_release))

        lib_extensions = ["*.a"]
        if self.settings.os == "Windows":
            lib_extensions = ["*.lib"]

        for lib_extension in lib_extensions:
            self.copy(lib_extension, dst="lib/Debug", src="{}/lib".format(build_artifacts_debug), keep_path=False)
            self.copy(lib_extension, dst="lib/Release", src="{}/lib".format(build_artifacts_release), keep_path=False)

        bin_extensions = ["*.so"]
        if self.settings.os == "Windows":
            bin_extensions = ["*.dll", "*.pdb"]
        if self.settings.os == "Macos":
            bin_extensions = ["*.dynlib"]

        for bin_extension in bin_extensions:
            self.copy(bin_extension, dst="bin/Debug", src="{}/bin".format(build_artifacts_debug), keep_path=False)
            self.copy(bin_extension, dst="bin/Release", src="{}/bin".format(build_artifacts_release), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        self.cpp_info.debug.includedirs = ["include_debug"]
        self.cpp_info.debug.libs = ["assimp-vc142-mtd", "IrrXMLd", "zlibd"]
        self.cpp_info.debug.libdirs = ["lib/Debug"]
        self.cpp_info.debug.bindirs = ["bin/Debug"]

        self.cpp_info.release.includedirs = ["include_release"]
        self.cpp_info.release.libs = ["assimp-vc142-mt", "IrrXML", "zlib"]
        self.cpp_info.release.libdirs = ["lib/Release"]
        self.cpp_info.release.bindirs = ["bin/Release"]
