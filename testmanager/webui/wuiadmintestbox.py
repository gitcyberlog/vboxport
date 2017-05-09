# -*- coding: utf-8 -*-
# $Id: wuiadmintestbox.py 53284 2014-11-10 12:03:49Z vboxsync $

"""
Test Manager WUI - TestBox.
"""

__copyright__ = \
"""
Copyright (C) 2012-2014 Oracle Corporation

This file is part of VirtualBox Open Source Edition (OSE), as
available from http://www.virtualbox.org. This file is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License (GPL) as published by the Free Software
Foundation, in version 2 as it comes in the "COPYING" file of the
VirtualBox OSE distribution. VirtualBox OSE is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY of any kind.

The contents of this file may alternatively be used under the terms
of the Common Development and Distribution License Version 1.0
(CDDL) only, as it comes in the "COPYING.CDDL" file of the
VirtualBox OSE distribution, in which case the provisions of the
CDDL are applicable instead of those of the GPL.

You may elect to license modified versions of this file under the
terms and conditions of either the GPL or the CDDL or both.
"""
__version__ = "$Revision: 53284 $"


# Standard python imports.
import socket;

# Validation Kit imports.
from testmanager.webui.wuicontentbase   import WuiListContentWithActionBase, WuiFormContentBase, WuiLinkBase, WuiSvnLink, \
                                               WuiTmLink, WuiSpanText, WuiRawHtml;
from testmanager.core.db                import TMDatabaseConnection;
from testmanager.core.schedgroup        import SchedGroupLogic, SchedGroupData;
from testmanager.core.testbox           import TestBoxData;
from testmanager.core.testset           import TestSetData;
from common                             import utils;
from testmanager.core.db                import isDbTimestampInfinity;


class WuiTestBox(WuiFormContentBase):
    """
    WUI TestBox Form Content Generator.
    """

    def __init__(self, oData, sMode, oDisp):
        if sMode == WuiFormContentBase.ksMode_Add:
            sTitle = 'Create TextBox';
            if oData.uuidSystem is not None and len(oData.uuidSystem) > 10:
                sTitle += ' - ' + oData.uuidSystem;
        elif sMode == WuiFormContentBase.ksMode_Edit:
            sTitle = 'Edit TestBox - %s (#%s)' % (oData.sName, oData.idTestBox);
        else:
            assert sMode == WuiFormContentBase.ksMode_Show;
            sTitle = 'TestBox - %s (#%s)' % (oData.sName, oData.idTestBox);
        WuiFormContentBase.__init__(self, oData, sMode, 'TestBox', oDisp, sTitle);

        # Try enter sName as hostname (no domain) when creating the testbox.
        if    sMode == WuiFormContentBase.ksMode_Add  \
          and self._oData.sName in [None, ''] \
          and self._oData.ip not in [None, '']:
            try:
                (self._oData.sName, _, _) = socket.gethostbyaddr(self._oData.ip);
            except:
                pass;
            offDot = self._oData.sName.find('.');
            if offDot > 0:
                self._oData.sName = self._oData.sName[:offDot];


    def _populateForm(self, oForm, oData):
        oForm.addIntRO(TestBoxData.ksParam_idTestBox, oData.idTestBox, 'TestBox ID');
        oForm.addIntRO(TestBoxData.ksParam_idGenTestBox, oData.idGenTestBox, 'TestBox generation ID');
        oForm.addTimestampRO(TestBoxData.ksParam_tsEffective, oData.tsEffective, 'Last changed');
        oForm.addTimestampRO(TestBoxData.ksParam_tsExpire, oData.tsExpire, 'Expires (excl)');
        oForm.addIntRO(TestBoxData.ksParam_uidAuthor, oData.uidAuthor, 'Changed by UID');

        oForm.addText(TestBoxData.ksParam_ip, oData.ip, 'TestBox IP Address');
        oForm.addUuid(TestBoxData.ksParam_uuidSystem, oData.uuidSystem, 'TestBox System/Firmware UUID');
        oForm.addText(TestBoxData.ksParam_sName, oData.sName, 'TestBox Name');
        oForm.addText(TestBoxData.ksParam_sDescription, oData.sDescription, \
            'TestBox Description');
        oForm.addComboBox(TestBoxData.ksParam_idSchedGroup, oData.idSchedGroup, \
            'Scheduling Group', SchedGroupLogic(\
                TMDatabaseConnection()).getSchedGroupsForCombo());
        oForm.addCheckBox(TestBoxData.ksParam_fEnabled, oData.fEnabled, 'Enabled');
        oForm.addComboBox(TestBoxData.ksParam_enmLomKind, oData.enmLomKind, \
            'Lights-out-management', TestBoxData.kaoLomKindDescs);
        oForm.addText(TestBoxData.ksParam_ipLom, oData.ipLom, \
            'Lights-out-management IP Address');
        oForm.addInt(TestBoxData.ksParam_pctScaleTimeout, oData.pctScaleTimeout, \
            'Timeout scale factor (%)');

        ## @todo Pretty format the read-only fields and use hidden fields for
        #        passing the actual values. (Yes, we need the values so we can
        #        display the form correctly on input error.)
        oForm.addTextRO(TestBoxData.ksParam_sOs, oData.sOs, 'TestBox OS');
        oForm.addTextRO(TestBoxData.ksParam_sOsVersion, oData.sOsVersion, 'TestBox OS version');
        oForm.addTextRO(TestBoxData.ksParam_sCpuArch, oData.sCpuArch, 'TestBox OS kernel architecture');
        oForm.addTextRO(TestBoxData.ksParam_sCpuVendor, oData.sCpuVendor, 'TestBox CPU vendor');
        oForm.addTextRO(TestBoxData.ksParam_sCpuName, oData.sCpuName, 'TestBox CPU name');
        if oData.lCpuRevision:
            oForm.addTextRO(TestBoxData.ksParam_lCpuRevision, '%#x' \
            % (oData.lCpuRevision,), 'TestBox CPU revision', \
            sPostHtml=' (family=%#x model=%#x stepping=%#x)' \
            % (oData.getCpuFamily(), oData.getCpuModel(), \
            oData.getCpuStepping(),), sSubClass='long');
        else:
            oForm.addLongRO(TestBoxData.ksParam_lCpuRevision, oData.lCpuRevision, 'TestBox CPU revision');
        oForm.addIntRO(TestBoxData.ksParam_cCpus, oData.cCpus, 'Number of CPUs, cores and threads');
        oForm.addCheckBoxRO(TestBoxData.ksParam_fCpuHwVirt, oData.fCpuHwVirt, 'VT-x or AMD-V supported');
        oForm.addCheckBoxRO(TestBoxData.ksParam_fCpuNestedPaging, oData.fCpuNestedPaging, 'Nested paging supported');
        oForm.addCheckBoxRO(TestBoxData.ksParam_fCpu64BitGuest, oData.fCpu64BitGuest, '64-bit guest supported');
        oForm.addCheckBoxRO(TestBoxData.ksParam_fChipsetIoMmu, oData.fChipsetIoMmu, 'I/O MMU supported');
        oForm.addMultilineTextRO(TestBoxData.ksParam_sReport, oData.sReport, 'Hardware/software report');
        oForm.addLongRO(TestBoxData.ksParam_cMbMemory, oData.cMbMemory, 'Installed RAM size (MB)');
        oForm.addLongRO(TestBoxData.ksParam_cMbScratch, oData.cMbScratch, 'Available scratch space (MB)');
        oForm.addIntRO(TestBoxData.ksParam_iTestBoxScriptRev, \
            oData.iTestBoxScriptRev, 'TestBox Script SVN revision');
        # Later:
        #if not self.isAttributeNull(''):
        #    sHexVer = '%s.%s.%.%s' % (oData.iPythonHexVersion >> 24,
        #    (oData.iPythonHexVersion >> 16) & 0xff,
        #                             (oData.iPythonHexVersion >> 8) & 0xff,
        #    oData.iPythonHexVersion & 0xff);
        #else:
        #    sHexVer = str(oData.iPythonHexVersion);

        oForm.addIntRO(TestBoxData.ksParam_iPythonHexVersion, \
            oData.iPythonHexVersion, 'Python version (hex)');
        if self._sMode == WuiFormContentBase.ksMode_Edit:
            oForm.addComboBox(TestBoxData.ksParam_enmPendingCmd, \
            oData.enmPendingCmd, 'Pending command', TestBoxData.kaoTestBoxCmdDescs);
        else:
            oForm.addComboBoxRO(TestBoxData.ksParam_enmPendingCmd, \
            oData.enmPendingCmd, 'Pending command', TestBoxData.kaoTestBoxCmdDescs);

        if self._sMode != WuiFormContentBase.ksMode_Show:
            oForm.addSubmit('Create TestBox' if self._sMode == WuiFormContentBase.ksMode_Add else 'Change TestBox');

        return True;


class WuiTestBoxList(WuiListContentWithActionBase):
    """
    WUI TestBox List Content Generator.
    """

    ## Descriptors for the combo box.
    kasTestBoxActionDescs = \
    [\
        ['none', 'Select an action...', ''],
        ['enable', 'Enable', ''],
        ['disable', 'Disable', ''],
        TestBoxData.kaoTestBoxCmdDescs[1],
        TestBoxData.kaoTestBoxCmdDescs[2],
        TestBoxData.kaoTestBoxCmdDescs[3],
        TestBoxData.kaoTestBoxCmdDescs[4],
        TestBoxData.kaoTestBoxCmdDescs[5],
    ];

    def __init__(self, aoEntries, iPage, cItemsPerPage, tsEffective, fnDPrint, oDisp):
        WuiListContentWithActionBase.__init__(self, aoEntries, iPage, cItemsPerPage, \
        tsEffective, sTitle='TestBoxes', sId='users', fnDPrint=fnDPrint, oDisp=oDisp);
        self._asColumnHeaders.extend(['Name', 'LOM', 'Status', 'Cmd', 'Script', \
            'Actions']);
        self._asColumnAttribs.extend(['align="center"', 'align="center"', \
            'align="center"', 'align="center"', 'align="center"', 'align="center"', \
            'align="center"', '', '', '', 'align="right"', 'align="right"', \
            'align="right"', 'align="center"']);
        self._aoActions = list(self.kasTestBoxActionDescs);
        self._aoSchedGroups = SchedGroupLogic(self._oDisp.getDb()).fetchOrderedByName();
        self._dSchedGroups = dict();
        for oSchedGroup in self._aoSchedGroups:
            self._aoActions.append(['setgroup-%u' % (oSchedGroup.idSchedGroup,), \
            'Migrate to group %s (#%u)' % (oSchedGroup.sName, \
            oSchedGroup.idSchedGroup,), oSchedGroup.sDescription]);
            self._dSchedGroups[oSchedGroup.idSchedGroup] = oSchedGroup;
        self._sAction = oDisp.ksActionTestBoxListPost;
        self._sCheckboxName = TestBoxData.ksParam_idTestBox;

    def _formatListEntry(self, iEntry): # pylint: disable=R0914
        from testmanager.webui.wuiadmin import WuiAdmin;
        oEntry = self._aoEntries[iEntry];

        # Lights outs managment.
        if oEntry.enmLomKind == TestBoxData.ksLomKind_ILOM:
            aoLom = [WuiLinkBase('ILOM', 'https://%s/' % (oEntry.ipLom,), \
            fBracketed=False),];
        elif oEntry.enmLomKind == TestBoxData.ksLomKind_ELOM:
            aoLom = [WuiLinkBase('ELOM', 'http://%s/'  % (oEntry.ipLom,), \
            fBracketed=False),];
        elif oEntry.enmLomKind == TestBoxData.ksLomKind_AppleXserveLom:
            aoLom = ['Apple LOM'];
        elif oEntry.enmLomKind == TestBoxData.ksLomKind_None:
            aoLom = ['none'];
        else:
            aoLom = ['Unexpected enmLomKind value "%s"' % (oEntry.enmLomKind,)];
        if oEntry.ipLom is not None:
            if oEntry.enmLomKind in [TestBoxData.ksLomKind_ILOM, \
                TestBoxData.ksLomKind_ELOM]:
                aoLom += [WuiLinkBase('(ssh)', 'ssh://%s' % (oEntry.ipLom,), \
                    fBracketed=False)];
            aoLom += [WuiRawHtml('<br>'), '%s' % (oEntry.ipLom,)];

        # State and Last seen.
        if oEntry.oStatus is None:
            oSeen = WuiSpanText('tmspan-offline', 'Never');
            oState = '';
        else:
            oDelta = oEntry.tsCurrent - oEntry.oStatus.tsUpdated;
            if oDelta.days <= 0 and oDelta.seconds <= 15*60: # 15 mins and we consider you dead.
                oSeen = WuiSpanText('tmspan-online', u'%s\u00a0s\u00a0ago' % (oDelta.days * 24 * 3600 + oDelta.seconds,));
            else:
                oSeen = WuiSpanText('tmspan-offline', u'%s' \
                    % (self.formatTsShort(oEntry.oStatus.tsUpdated),));

            if oEntry.oStatus.idTestSet is None:
                oState = str(oEntry.oStatus.enmState);
            else:
                from testmanager.webui.wuimain import WuiMain;
                oState = WuiTmLink(oEntry.oStatus.enmState, WuiMain.ksScriptName, \
                {WuiMain.ksParamAction: WuiMain.ksActionTestResultDetails, \
                TestSetData.ksParam_idTestSet: oEntry.oStatus.idTestSet,}, \
                sTitle='#%u' % (oEntry.oStatus.idTestSet,), fBracketed=False);

        # Group link.
        oGroup = self._dSchedGroups.get(oEntry.idSchedGroup);
        oGroupLink = WuiTmLink(oGroup.sName if oGroup is not None else \
            str(oEntry.idSchedGroup), WuiAdmin.ksScriptName, \
                {WuiAdmin.ksParamAction: WuiAdmin.ksActionSchedGroupEdit, \
                SchedGroupData.ksParam_idSchedGroup: oEntry.idSchedGroup,}, \
                sTitle='#%u' % (oEntry.idSchedGroup,), fBracketed=False);

        # Reformat the OS version to take less space.
        aoOs = ['N/A'];
        if oEntry.sOs is not None and oEntry.sOsVersion is not None and \
            oEntry.sCpuArch:
            sOsVersion = oEntry.sOsVersion;
            if sOsVersion[0] not in ['v', 'V', 'r', 'R'] \
                and sOsVersion[0].isdigit() \
                and sOsVersion.find('.') in range(4) \
                and oEntry.sOs in ['linux', 'solaris', 'darwin',]:
                sOsVersion = 'v' + sOsVersion;

            sVer1 = sOsVersion;
            sVer2 = None;
            if oEntry.sOs == 'linux' or oEntry.sOs == 'darwin':
                iSep = sOsVersion.find(' / ');
                if iSep > 0:
                    sVer1 = sOsVersion[:iSep].strip();
                    sVer2 = sOsVersion[iSep + 3:].strip();
                    sVer2 = sVer2.replace('Red Hat Enterprise Linux Server', 'RHEL');
                    sVer2 = sVer2.replace('Oracle Linux Server', 'OL');
            elif oEntry.sOs == 'solaris':
                iSep = sOsVersion.find(' (');
                if iSep > 0 and sOsVersion[-1] == ')':
                    sVer1 = sOsVersion[:iSep].strip();
                    sVer2 = sOsVersion[iSep + 2:-1].strip();
            aoOs = [WuiSpanText('tmspan-osarch', u'%s.%s' \
                % (oEntry.sOs, oEntry.sCpuArch,)), WuiSpanText('tmspan-osver1', \
                sVer1.replace('-', u'\u2011'),),];
            if sVer2 is not None:
                aoOs += [WuiRawHtml('<br>'), WuiSpanText('tmspan-osver2', \
                sVer2.replace('-', u'\u2011')),];

        # Format the CPU revision.
        oCpu = None;
        if oEntry.lCpuRevision is not None and oEntry.sCpuVendor is not None and \
            oEntry.sCpuName is not None:
            oCpu = [u'%s (fam:%xh\u00a0m:%xh\u00a0s:%xh)' \
            % (oEntry.sCpuVendor, oEntry.getCpuFamily(), oEntry.getCpuModel(), \
                oEntry.getCpuStepping(),), WuiRawHtml('<br>'), oEntry.sCpuName,];
        else:
            oCpu = [];
            if oEntry.sCpuVendor is not None:
                oCpu.append(oEntry.sCpuVendor);
            if oEntry.lCpuRevision is not None:
                oCpu.append('%#x' % (oEntry.lCpuRevision,));
            if oEntry.sCpuName is not None:
                oCpu.append(oEntry.sCpuName);

        # Stuff cpu vendor and cpu/box features into one field.
        asFeatures = []
        if oEntry.fCpuHwVirt is True: asFeatures.append(u'HW\u2011Virt');
        if oEntry.fCpuNestedPaging is True: asFeatures.append(u'Nested\u2011Paging');
        if oEntry.fCpu64BitGuest is True: asFeatures.append(u'64\u2011bit\u2011Guest');
        if oEntry.fChipsetIoMmu is True: asFeatures.append(u'I/O\u2011MMU');
        sFeatures = u' '.join(asFeatures) if len(asFeatures) > 0 else u'';

        # Collection applicable actions.
        aoActions = [\
             WuiTmLink('Details', WuiAdmin.ksScriptName, \
             {WuiAdmin.ksParamAction: WuiAdmin.ksActionTestBoxDetails, \
             TestBoxData.ksParam_idTestBox: oEntry.idTestBox, \
             WuiAdmin.ksParamEffectiveDate: self._tsEffectiveDate,}),\
        ]

        if isDbTimestampInfinity(oEntry.tsExpire):
            aoActions += [\
                WuiTmLink('Edit', WuiAdmin.ksScriptName, \
                    {WuiAdmin.ksParamAction: WuiAdmin.ksActionTestBoxEdit, \
                    TestBoxData.ksParam_idTestBox: oEntry.idTestBox,}),
                WuiTmLink('Remove', WuiAdmin.ksScriptName, \
                    {WuiAdmin.ksParamAction: WuiAdmin.ksActionTestBoxRemovePost, \
                    TestBoxData.ksParam_idTestBox: oEntry.idTestBox}, \
                    sConfirm='Are you sure that you want to remove %s (%s)?' \
                    % (oEntry.sName, oEntry.ip)),\
            ]

        if oEntry.sOs not in ['win', 'os2',] and oEntry.ip is not None:
            aoActions.append(WuiLinkBase('ssh', 'ssh://vbox@%s' % (oEntry.ip,),));

        return [self._getCheckBoxColumn(iEntry, oEntry.idTestBox), \
            [WuiSpanText('tmspan-name', oEntry.sName), WuiRawHtml('<br>'), '%s' \
                % (oEntry.ip,),], aoLom, \
            ['' if oEntry.fEnabled else 'disabled / ', oState, WuiRawHtml('<br>'), \
                oSeen,], oEntry.enmPendingCmd, WuiSvnLink(oEntry.iTestBoxScriptRev), \
            oEntry.formatPythonVersion(), oGroupLink, aoOs, oCpu, sFeatures, \
            oEntry.cCpus if oEntry.cCpus is not None else 'N/A', \
            utils.formatNumberNbsp(oEntry.cMbMemory) + u'\u00a0MB' if \
            oEntry.cMbMemory is not None else 'N/A', \
            utils.formatNumberNbsp(oEntry.cMbScratch) + u'\u00a0MB' if \
            oEntry.cMbScratch is not None else 'N/A', aoActions,\
        ];

