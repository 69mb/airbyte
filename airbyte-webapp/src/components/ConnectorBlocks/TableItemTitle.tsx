import React from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, DropDownRow, H3, H5 } from "components";
import { Popout } from "components/base/Popout/Popout";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { ReleaseStage } from "core/domain/connector";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";

type IProps = {
  type: "source" | "destination";
  dropDownData: DropDownRow.IDataItem[];
  onSelect: (item: DropDownRow.IDataItem) => void;
  entity: string;
  entityName: string;
  entityIcon?: React.ReactNode;
  releaseStage?: ReleaseStage;
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px 18px 27px;
`;

const EntityType = styled(H5)`
  display: flex;
  gap: 6px;
  align-items: center;
  color: ${({ theme }) => theme.greyColor55};
`;

const EntityInfo = styled(Content)`
  justify-content: left;
  padding-top: 15px;
  padding-bottom: 39px;
  gap: 15px;
`;

const EntityIcon = styled.div`
  height: 40px;
  width: 40px;
`;

const TableItemTitle: React.FC<IProps> = ({
  type,
  dropDownData,
  onSelect,
  entity,
  entityName,
  entityIcon,
  releaseStage,
}) => {
  const { hasFeature } = useFeatureService();
  const allowCreateConnection = hasFeature(FeatureItem.AllowCreateConnection);
  const formatMessage = useIntl().formatMessage;
  const options = [
    {
      label: formatMessage({
        id: `tables.${type}AddNew`,
      }),
      value: "create-new-item",
      primary: true,
    },
    ...dropDownData,
  ];

  return (
    <>
      <EntityInfo>
        {entityIcon && <EntityIcon>{entityIcon}</EntityIcon>}
        <div>
          <H3 bold>{entityName}</H3>
          <EntityType>
            <span>{entity}</span>
            <ReleaseStageBadge stage={releaseStage} />
          </EntityType>
        </div>
      </EntityInfo>
      <Content>
        <H5>
          <FormattedMessage id="tables.connections" />
        </H5>
        <Popout
          data-testid={`select-${type}`}
          options={options}
          isSearchable={false}
          styles={{
            // TODO: hack to position select
            menuPortal: (base) => ({
              ...base,
              "margin-left": "-130px",
            }),
          }}
          onChange={onSelect}
          targetComponent={({ onOpen }) => (
            <Button onClick={onOpen} disabled={!allowCreateConnection}>
              <FormattedMessage id={`tables.${type}Add`} />
            </Button>
          )}
        />
      </Content>
    </>
  );
};

export default TableItemTitle;
