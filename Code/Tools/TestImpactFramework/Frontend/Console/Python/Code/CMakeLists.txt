#
# Copyright (c) Contributors to the Open 3D Engine Project.
# For complete copyright and license terms please see the LICENSE at the root of this distribution.
#
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#

if(LY_MONOLITHIC_GAME)
    return()
endif()

ly_add_target(
    NAME TestImpact.Frontend.Console.Python.Static STATIC
    NAMESPACE AZ
    FILES_CMAKE
        testimpactframework_frontend_console_python_static_files.cmake
    INCLUDE_DIRECTORIES
        PUBLIC
            Include
        PRIVATE
            Source
    COMPILE_DEFINITIONS
        PRIVATE
            ${LY_TEST_IMPACT_CONFIG_FILE_PATH_DEFINITION}
    BUILD_DEPENDENCIES
        PRIVATE
            AZ::TestImpact.Frontend.Console.Common.Static
            AZ::TestImpact.Runtime.Python.Static
        PUBLIC
            AZ::TestImpact.Frontend.Console.Common.Headers
)

ly_add_target(
    NAME TestImpact.Frontend.Console.Python EXECUTABLE
    OUTPUT_NAME tiaf_py
    NAMESPACE AZ
    FILES_CMAKE
        testimpactframework_frontend_console_python_files.cmake
    INCLUDE_DIRECTORIES
        PRIVATE
            Source
    BUILD_DEPENDENCIES
        PRIVATE
            AZ::TestImpact.Frontend.Console.Python.Static
)
