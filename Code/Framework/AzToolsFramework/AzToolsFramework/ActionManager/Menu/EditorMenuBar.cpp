/*
 * Copyright (c) Contributors to the Open 3D Engine Project.
 * For complete copyright and license terms please see the LICENSE at the root of this distribution.
 *
 * SPDX-License-Identifier: Apache-2.0 OR MIT
 *
 */

#include <AzToolsFramework/ActionManager/Menu/EditorMenuBar.h>
#include <AzToolsFramework/ActionManager/Menu/MenuManagerInterface.h>

#include <QMenuBar>

namespace AzToolsFramework
{
    EditorMenuBar::EditorMenuBar()
        : m_menuBar(new QMenuBar(m_defaultParentWidget))
    {
    }
    
    void EditorMenuBar::AddMenu(int sortKey, AZStd::string menuIdentifier)
    {
        m_menuToSortKeyMap.insert(AZStd::make_pair(menuIdentifier, sortKey));
        m_menus[sortKey].push_back(AZStd::move(menuIdentifier));
    }
    
    bool EditorMenuBar::ContainsMenu(const AZStd::string& menuIdentifier) const
    {
        return m_menuToSortKeyMap.contains(menuIdentifier);
    }

    AZStd::optional<int> EditorMenuBar::GetMenuSortKey(const AZStd::string& menuIdentifier) const
    {
        auto menuIterator = m_menuToSortKeyMap.find(menuIdentifier);
        if (menuIterator == m_menuToSortKeyMap.end())
        {
            return AZStd::nullopt;
        }

        return menuIterator->second;
    }

    QMenuBar* EditorMenuBar::GetMenuBar()
    {
        return m_menuBar;
    }

    const QMenuBar* EditorMenuBar::GetMenuBar() const
    {
        return m_menuBar;
    }

    void EditorMenuBar::RefreshMenuBar()
    {
        m_menuBar->clear();

        for (const auto& vectorIterator : m_menus)
        {
            for (const auto& menuIdentifier : vectorIterator.second)
            {
                if (QMenu* menu = m_menuManagerInternalInterface->GetMenu(menuIdentifier))
                {
                    m_menuBar->addMenu(menu);
                }
            }
        }
    }

    void EditorMenuBar::Initialize(QWidget* defaultParentWidget)
    {
        m_defaultParentWidget = defaultParentWidget;

        m_menuManagerInterface = AZ::Interface<MenuManagerInterface>::Get();
        AZ_Assert(m_menuManagerInterface, "EditorMenuBar - Could not retrieve instance of MenuManagerInterface");

        m_menuManagerInternalInterface = AZ::Interface<MenuManagerInternalInterface>::Get();
        AZ_Assert(m_menuManagerInternalInterface, "EditorMenuBar - Could not retrieve instance of MenuManagerInternalInterface");
    }

    void EditorMenuBar::Reflect(AZ::ReflectContext* context)
    {
        if (auto serializeContext = azrtti_cast<AZ::SerializeContext*>(context))
        {
            serializeContext->Class<EditorMenuBar>()->Field("Menus", &EditorMenuBar::m_menus);
        }
    }

} // namespace AzToolsFramework
